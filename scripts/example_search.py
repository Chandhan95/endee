#!/usr/bin/env python3
"""Example script demonstrating RAG system usage"""

import asyncio
import logging

from src.rag_service import RAGService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate RAG system capabilities"""
    
    # Initialize RAG service
    logger.info("Initializing RAG service...")
    rag_service = RAGService()
    
    try:
        await rag_service.initialize()
        logger.info("✓ RAG service initialized")
        
        # Test queries
        queries = [
            "What are the main features of Python?",
            "How do vector databases work?",
            "What is RAG and how does it work?",
            "What distance metrics are used in vector databases?",
            "Tell me about Endee vector database",
        ]
        
        logger.info(f"\n{'='*60}")
        logger.info("Running semantic search queries...")
        logger.info(f"{'='*60}\n")
        
        for query in queries:
            logger.info(f"Query: {query}")
            logger.info("-" * 60)
            
            result = await rag_service.search(
                query=query,
                top_k=3,
                use_llm=False  # Set to True if OpenAI API is configured
            )
            
            logger.info(f"Results found: {result['result_count']}")
            logger.info(f"Retrieval time: {result['retrieval_time_ms']:.2f}ms")
            logger.info(f"Total time: {result['total_time_ms']:.2f}ms")
            
            if result['results']:
                logger.info("\nTop results:")
                for i, res in enumerate(result['results'][:2], 1):
                    metadata = res.get('metadata', {})
                    content = metadata.get('content', '')[:100]
                    score = res.get('score', 'N/A')
                    logger.info(f"  {i}. Score: {score}, Content: {content}...")
            
            if result['generated_answer']:
                logger.info(f"\nGenerated Answer:\n{result['generated_answer']}")
            
            logger.info()
        
        logger.info(f"{'='*60}")
        logger.info("Search examples completed successfully!")
        logger.info(f"{'='*60}")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
