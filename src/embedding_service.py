"""Document embedding and chunking service"""

import logging
from typing import List, Dict, Any
from uuid import uuid4
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings and processing documents"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service
        
        Args:
            model_name: Name of the sentence-transformer model to use
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Dimension: {self.dimension}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()
    
    def chunk_document(
        self,
        document_name: str,
        content: str,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Split document into overlapping chunks
        
        Args:
            document_name: Name/identifier of the document
            content: Document content
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of document chunks with metadata
        """
        chunks = []
        step = chunk_size - overlap
        
        i = 0
        while i < len(content):
            end = min(i + chunk_size, len(content))
            chunk_content = content[i:end]
            
            chunks.append({
                "id": str(uuid4()),
                "content": chunk_content,
                "metadata": {
                    "document_name": document_name,
                    "chunk_index": len(chunks),
                    "original_length": len(content),
                    "start_pos": i,
                    "end_pos": end,
                }
            })
            
            if end >= len(content):
                break
            
            i += step
        
        logger.info(f"Split document '{document_name}' into {len(chunks)} chunks")
        return chunks
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "model": self.model_name,
            "dimension": self.dimension
        }
