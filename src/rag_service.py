"""RAG (Retrieval-Augmented Generation) service"""

import logging
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI

from src.endee_client import EndeeClient
from src.embedding_service import EmbeddingService
from src.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    """Orchestrates RAG pipeline: ingestion, embedding, storage, retrieval"""
    
    def __init__(
        self,
        index_name: str = "documents",
        embedding_model: Optional[str] = None
    ):
        """
        Initialize RAG service
        
        Args:
            index_name: Name of the vector index
            embedding_model: Name of embedding model to use
        """
        self.index_name = index_name
        self.embedding_service = EmbeddingService(
            embedding_model or settings.embedding_model
        )
        self.endee_client = EndeeClient(
            base_url=settings.endee_base_url,
            auth_token=settings.endee_auth_token,
            timeout=settings.endee_timeout
        )
        
        # Initialize OpenAI client if configured
        self.openai_client = None
        if settings.openai_api_key:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
            logger.info("OpenAI client initialized")
    
    async def initialize(self) -> None:
        """Initialize RAG system by creating index"""
        logger.info("Initializing RAG system...")
        
        # Wait for Endee to be available
        max_retries = 10
        for attempt in range(max_retries):
            if self.endee_client.health_check():
                logger.info("Endee server is healthy")
                break
            logger.info(f"Waiting for Endee server... (attempt {attempt + 1}/{max_retries})")
            time.sleep(1)
        else:
            raise RuntimeError("Endee server is not responding")
        
        # Create index
        model_info = self.embedding_service.get_model_info()
        self.endee_client.create_index(
            name=self.index_name,
            dimension=model_info["dimension"],
            metric="cosine"
        )
        
        logger.info("RAG system initialized successfully")
    
    async def ingest_document(
        self,
        document_name: str,
        content: str,
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a document into the RAG system
        
        Args:
            document_name: Name of the document
            content: Document content
            source_url: Optional URL source of the document
            
        Returns:
            Ingestion result with chunk count
        """
        logger.info(f"Ingesting document: {document_name}")
        
        # Split into chunks
        chunks = self.embedding_service.chunk_document(
            document_name=document_name,
            content=content,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        
        # Generate embeddings
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_service.embed_texts(texts)
        
        # Prepare vectors
        vectors = []
        for chunk, embedding in zip(chunks, embeddings):
            vectors.append({
                "id": chunk["id"],
                "values": embedding,
                "metadata": {
                    **chunk["metadata"],
                    "content": chunk["content"],
                    "source_url": source_url,
                }
            })
        
        # Insert into Endee
        self.endee_client.insert(self.index_name, vectors)
        logger.info(f"Inserted {len(vectors)} vectors for document '{document_name}'")
        
        return {
            "document_name": document_name,
            "chunks_added": len(vectors),
            "total_content_length": len(content)
        }
    
    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_llm: bool = False
    ) -> Dict[str, Any]:
        """
        Semantic search in ingested documents
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_llm: Whether to generate LLM answer
            
        Returns:
            Search results with optional generated answer
        """
        start_time = time.time()
        top_k = top_k or settings.top_k_results
        
        logger.info(f"Searching for: {query}")
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        retrieval_start = time.time()
        
        # Search in Endee
        results = self.endee_client.search(
            index_name=self.index_name,
            query_vector=query_embedding,
            k=top_k
        )
        
        retrieval_time = (time.time() - retrieval_start) * 1000  # ms
        
        # Generate answer with LLM if requested
        generated_answer = None
        if use_llm and results and self.openai_client:
            generated_answer = await self._generate_answer(query, results)
        
        total_time = (time.time() - start_time) * 1000  # ms
        
        return {
            "query": query,
            "results": results,
            "generated_answer": generated_answer,
            "retrieval_time_ms": retrieval_time,
            "total_time_ms": total_time,
            "result_count": len(results)
        }
    
    async def _generate_answer(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            query: Original query
            results: Retrieved search results
            
        Returns:
            Generated answer
        """
        if not self.openai_client:
            return "LLM not configured"
        
        # Build context from results
        context_parts = []
        for i, result in enumerate(results[:3], 1):  # Use top 3
            content = result.get("metadata", {}).get("content", "")
            if content:
                context_parts.append(f"[Document {i}]:\n{content[:300]}...")
        
        context = "\n\n".join(context_parts)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers questions based on provided documents. Be concise and accurate."
                    },
                    {
                        "role": "user",
                        "content": f"Based on the following documents, answer the query:\n\nQuery: {query}\n\nContext:\n{context}"
                    }
                ],
                max_tokens=settings.openai_max_tokens,
                temperature=settings.openai_temperature
            )
            
            return response.choices[0].message.content or "Unable to generate answer"
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "Error generating answer"
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            stats = self.endee_client.get_index_stats(self.index_name)
            return stats
        except Exception as e:
            logger.error(f"Error fetching statistics: {str(e)}")
            return {"error": "Unable to fetch statistics"}
    
    def list_indices(self) -> List[str]:
        """List all available indices"""
        return self.endee_client.list_indices()
