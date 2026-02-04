"""FastAPI application for the RAG system"""

import logging
from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import settings
from src.rag_service import RAGService

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global RAG service instance
rag_service: Optional[RAGService] = None


# Pydantic models
class SearchRequest(BaseModel):
    """Request model for search"""
    query: str
    top_k: Optional[int] = None
    use_llm: bool = False


class SearchResponse(BaseModel):
    """Response model for search"""
    query: str
    results: List[dict]
    generated_answer: Optional[str] = None
    retrieval_time_ms: float
    total_time_ms: float
    result_count: int


class DocumentIngestionResponse(BaseModel):
    """Response model for document ingestion"""
    document_name: str
    chunks_added: int
    total_content_length: int


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    rag_initialized: bool
    endee_connected: bool


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    global rag_service
    logger.info("Starting RAG system...")
    
    rag_service = RAGService(
        index_name="documents",
        embedding_model=settings.embedding_model
    )
    
    try:
        await rag_service.initialize()
        logger.info("RAG system started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG system...")


# Create FastAPI app
app = FastAPI(
    title="Endee RAG System",
    description="AI-powered Retrieval Augmented Generation using Endee vector database",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    endee_connected = rag_service.endee_client.health_check()
    
    return HealthResponse(
        status="healthy" if endee_connected else "degraded",
        rag_initialized=True,
        endee_connected=endee_connected
    )


@app.post("/api/v1/ingest", response_model=DocumentIngestionResponse)
async def ingest_document(
    document_name: str = Form(...),
    content: str = Form(...),
    source_url: Optional[str] = Form(None)
) -> DocumentIngestionResponse:
    """
    Ingest a document into the RAG system
    
    Args:
        document_name: Name/identifier of the document
        content: Document content (text)
        source_url: Optional source URL
        
    Returns:
        Ingestion result
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    if not document_name or not content:
        raise HTTPException(status_code=400, detail="document_name and content are required")
    
    try:
        result = await rag_service.ingest_document(
            document_name=document_name,
            content=content,
            source_url=source_url
        )
        return DocumentIngestionResponse(**result)
    except Exception as e:
        logger.error(f"Error ingesting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ingest-file")
async def ingest_file(
    file: UploadFile = File(...),
    source_url: Optional[str] = None
) -> DocumentIngestionResponse:
    """
    Ingest a text file into the RAG system
    
    Args:
        file: Text file to ingest
        source_url: Optional source URL
        
    Returns:
        Ingestion result
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        
        result = await rag_service.ingest_document(
            document_name=file.filename or "document",
            content=content_str,
            source_url=source_url
        )
        return DocumentIngestionResponse(**result)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except Exception as e:
        logger.error(f"Error ingesting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """
    Semantic search in ingested documents
    
    Args:
        request: Search request with query and options
        
    Returns:
        Search results
    """
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    if not request.query:
        raise HTTPException(status_code=400, detail="query is required")
    
    try:
        result = await rag_service.search(
            query=request.query,
            top_k=request.top_k,
            use_llm=request.use_llm
        )
        return SearchResponse(**result)
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/statistics")
async def get_statistics() -> dict:
    """Get RAG system statistics"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    return await rag_service.get_statistics()


@app.get("/api/v1/indices")
async def list_indices() -> dict:
    """List all available indices"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    indices = rag_service.list_indices()
    return {
        "indices": indices,
        "count": len(indices)
    }


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information"""
    return {
        "name": "Endee RAG System",
        "version": "1.0.0",
        "description": "AI-powered Retrieval Augmented Generation using Endee vector database",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "ingest": "POST /api/v1/ingest",
            "ingest_file": "POST /api/v1/ingest-file",
            "search": "POST /api/v1/search",
            "statistics": "GET /api/v1/statistics",
            "indices": "GET /api/v1/indices"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
