"""Unit and integration tests for RAG system"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.endee_client import EndeeClient
from src.embedding_service import EmbeddingService
from src.rag_service import RAGService


class TestEndeeClient:
    """Test EndeeClient functionality"""
    
    def test_init_with_auth(self):
        """Test client initialization with authentication"""
        client = EndeeClient(
            base_url="http://localhost:8080",
            auth_token="test-token"
        )
        assert client.auth_token == "test-token"
        assert "Authorization" in client.headers
    
    def test_init_without_auth(self):
        """Test client initialization without authentication"""
        client = EndeeClient(base_url="http://localhost:8080")
        assert client.auth_token is None
        assert "Authorization" not in client.headers


class TestEmbeddingService:
    """Test EmbeddingService functionality"""
    
    def test_init(self):
        """Test embedding service initialization"""
        service = EmbeddingService()
        assert service.model is not None
        assert service.dimension == 384
    
    def test_chunk_document(self):
        """Test document chunking"""
        service = EmbeddingService()
        content = "Hello world. " * 100
        
        chunks = service.chunk_document(
            document_name="test",
            content=content,
            chunk_size=100,
            overlap=10
        )
        
        assert len(chunks) > 0
        assert all("id" in chunk for chunk in chunks)
        assert all("content" in chunk for chunk in chunks)
        assert all("metadata" in chunk for chunk in chunks)
    
    def test_embed_text(self):
        """Test text embedding"""
        service = EmbeddingService()
        embedding = service.embed_text("Hello world")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)


class TestRAGService:
    """Test RAGService functionality"""
    
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test RAG service initialization"""
        with patch.object(EndeeClient, 'health_check', return_value=True):
            with patch.object(EndeeClient, 'create_index'):
                service = RAGService()
                await service.initialize()
                # Service should be ready
                assert service.endee_client is not None
    
    @pytest.mark.asyncio
    async def test_search_basic(self):
        """Test basic search without LLM"""
        service = RAGService()
        
        # Mock the Endee search
        mock_results = [
            {
                "id": "chunk1",
                "score": 0.95,
                "metadata": {"content": "Test content"}
            }
        ]
        
        with patch.object(
            service.endee_client,
            'search',
            return_value=mock_results
        ):
            result = await service.search(
                query="test query",
                top_k=5,
                use_llm=False
            )
            
            assert "results" in result
            assert "query" in result
            assert result["query"] == "test query"
            assert len(result["results"]) > 0


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete ingestion and search pipeline"""
        # This would require a running Endee instance
        # Can be run with: pytest -m integration
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
