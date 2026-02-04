# Endee RAG System

**An AI-powered Retrieval-Augmented Generation (RAG) system using Endee vector database for semantic search and intelligent document processing.**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Project Overview

This project demonstrates a production-ready AI/ML application that leverages **Endee** as the vector database backbone for semantic search and RAG capabilities. It showcases how to:

- **Store and search embeddings** efficiently using Endee's high-performance vector database
- **Implement semantic search** to find contextually relevant documents
- **Build RAG systems** that combine retrieval with LLM-based answer generation
- **Process documents** at scale with chunking and embedding strategies
- **Integrate with LLMs** for intelligent question-answering

### Problem Statement

Traditional keyword-based search systems struggle with semantic understanding. This system solves this by:

1. **Converting documents to semantic embeddings** - capturing meaning, not just keywords
2. **Enabling similarity-based search** - finding conceptually related content
3. **Providing contextual answers** - using retrieved documents with LLMs for intelligent responses
4. **Scaling efficiently** - handling large document collections with Endee's performance

## 🏗️ System Architecture

### Technical Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Query / Documents                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   Embedding Service             │
        │  (sentence-transformers)        │
        │  - Text to Vector conversion    │
        │  - Document chunking            │
        │  - Batch processing             │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────────────┐
        │    Endee Vector Database                │
        │  - Store embeddings                     │
        │  - Cosine/L2 similarity search          │
        │  - Metadata filtering                   │
        │  - Index management                     │
        └────────────────┬────────────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   RAG Service Layer             │
        │  - Orchestration                │
        │  - Document ingestion           │
        │  - Search & retrieval           │
        │  - LLM integration              │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   FastAPI REST API              │
        │  - /api/v1/ingest               │
        │  - /api/v1/search               │
        │  - /api/v1/statistics           │
        │  - /docs (auto docs)            │
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   Optional: LLM Integration     │
        │   - OpenAI API                  │
        │   - Ollama (local)              │
        │   - Answer generation           │
        └────────────────────────────────┘
```

### How Endee is Used

1. **Index Management**: Create and manage vector indices for document embeddings
2. **Vector Storage**: Store document chunk embeddings with metadata (document name, content, source)
3. **Similarity Search**: Find k-nearest neighbors using cosine distance metric
4. **Metadata Filtering**: Optional filtering based on document properties
5. **Scalability**: Efficiently handle millions of vectors with SIMD optimizations

### Key Components

| Component | Purpose |
|-----------|---------|
| `EndeeClient` | HTTP client for Endee API (create index, insert vectors, search) |
| `EmbeddingService` | Generate embeddings using sentence-transformers, chunk documents |
| `RAGService` | Orchestrate ingestion, search, and LLM answer generation |
| `FastAPI App` | REST API with document upload, search, and statistics endpoints |

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Endee vector database running (Docker recommended)
- Optional: OpenAI API key for LLM features
- 4GB+ RAM recommended

### 1. Setup Endee Vector Database

#### Using Docker (Recommended)

```bash
# Pull and run Endee from Docker Hub
docker run -p 8080:8080 -v endee-data:/data endeeio/endee-server:latest
```

#### Or build locally
```bash
git clone https://github.com/EndeeLabs/endee.git
cd endee
./install.sh --release --avx2
./run.sh
```

**Verify Endee is running:**
```bash
curl http://localhost:8080/api/v1/health
```

### 2. Install Python Dependencies

```bash
# Clone this repository
git clone https://github.com/your-username/endee-rag-system.git
cd endee-rag-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional):
# ENDEE_BASE_URL=http://localhost:8080
# OPENAI_API_KEY=your_api_key_here (for LLM features)
```

### 4. Ingest Sample Documents

```bash
python -m scripts.ingest_samples
```

This ingests sample documents about Python, vector databases, and RAG systems.

### 5. Start the API Server

```bash
# Run with auto-reload during development
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or use the shortcut if configured
python src/main.py
```

The API will be available at `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### 6. Try Example Searches

```bash
# Run example search script
python -m scripts.example_search
```

Or use curl:

```bash
# Semantic search without LLM
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "top_k": 3, "use_llm": false}'

# Semantic search with LLM-generated answer (requires OPENAI_API_KEY)
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do vector databases work?", "top_k": 5, "use_llm": true}'
```

## 📡 API Documentation

### Endpoints

#### Health Check
```
GET /health
```

Returns system health status.

**Example Response:**
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "endee_connected": true
}
```

#### Ingest Document (Form Data)
```
POST /api/v1/ingest
```

Ingest a document via form data.

**Parameters:**
- `document_name` (string, required): Document identifier
- `content` (string, required): Document text content
- `source_url` (string, optional): Source URL of the document

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "document_name=my_doc" \
  -F "content=This is document content" \
  -F "source_url=https://example.com"
```

**Example Response:**
```json
{
  "document_name": "my_doc",
  "chunks_added": 1,
  "total_content_length": 24
}
```

#### Ingest File
```
POST /api/v1/ingest-file
```

Ingest a text file.

**Parameters:**
- `file` (file, required): Text file to upload
- `source_url` (string, optional): Source URL

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest-file" \
  -F "file=@document.txt"
```

#### Semantic Search
```
POST /api/v1/search
```

Search documents using semantic similarity.

**Request Body:**
```json
{
  "query": "your search query",
  "top_k": 5,
  "use_llm": false
}
```

**Parameters:**
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results (default: 5)
- `use_llm` (boolean, optional): Generate LLM answer (default: false, requires OPENAI_API_KEY)

**Example Response:**
```json
{
  "query": "What is Python?",
  "results": [
    {
      "id": "chunk-uuid",
      "score": 0.87,
      "metadata": {
        "document_name": "Python Guide",
        "chunk_index": 0,
        "content": "Python is a high-level programming language...",
        "source_url": null
      }
    }
  ],
  "generated_answer": null,
  "retrieval_time_ms": 45.23,
  "total_time_ms": 89.15,
  "result_count": 1
}
```

#### Get Statistics
```
GET /api/v1/statistics
```

Get system and index statistics.

**Example Response:**
```json
{
  "index_name": "documents",
  "vector_count": 42,
  "dimension": 384,
  "metric": "cosine"
}
```

#### List Indices
```
GET /api/v1/indices
```

List all available vector indices.

**Example Response:**
```json
{
  "indices": ["documents"],
  "count": 1
}
```

## 🔧 Configuration

Edit `.env` file to customize:

```env
# Endee Configuration
ENDEE_BASE_URL=http://localhost:8080          # Endee server URL
ENDEE_AUTH_TOKEN=                              # Optional auth token

# API Configuration
API_HOST=0.0.0.0                              # API host
API_PORT=8000                                 # API port
API_RELOAD=true                               # Hot reload in dev

# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2              # HuggingFace model
EMBEDDING_DIMENSION=384                       # Vector dimension

# Document Processing
CHUNK_SIZE=512                                # Characters per chunk
CHUNK_OVERLAP=50                              # Overlap between chunks
TOP_K_RESULTS=5                               # Default search results

# LLM Configuration
OPENAI_API_KEY=sk-...                         # OpenAI API key
OPENAI_MODEL=gpt-3.5-turbo                    # GPT model to use
OPENAI_TEMPERATURE=0.7                        # Response creativity
OPENAI_MAX_TOKENS=500                         # Max answer length

# Logging
LOG_LEVEL=INFO                                # Log level
ENVIRONMENT=development                       # Environment
```

## 📊 Use Cases Demonstrated

### 1. **Semantic Search**
Find documents similar to a query based on meaning, not keywords.
```python
result = await rag_service.search("How do neural networks work?", top_k=5)
```

### 2. **RAG (Retrieval-Augmented Generation)**
Combine document retrieval with LLM for accurate, contextual answers.
```python
result = await rag_service.search("What is machine learning?", use_llm=True)
```

### 3. **Document Intelligence**
Extract insights and answer questions about document collections.

### 4. **Recommendation Systems**
Find similar documents or content based on user preferences.

## 🧪 Testing & Examples

### Run Sample Data Ingestion
```bash
python -m scripts.ingest_samples
```

Ingests:
- Python Programming Guide
- Vector Databases Overview
- RAG Systems Explanation

### Run Search Examples
```bash
python -m scripts.example_search
```

Tests various queries and displays:
- Retrieval time
- Result count
- Top matching chunks
- Generated answers (if configured)

## 🔍 How Endee is Used in Detail

### Initialization
```python
# Create index with specified dimension
endee_client.create_index(
    name="documents",
    dimension=384,  # all-MiniLM-L6-v2 output dimension
    metric="cosine" # or "L2", "dot"
)
```

### Document Ingestion
```python
# Split document into chunks
chunks = embedding_service.chunk_document(
    document_name="myfile",
    content="...",
    chunk_size=512,
    overlap=50
)

# Generate embeddings
embeddings = embedding_service.embed_texts(
    [chunk["content"] for chunk in chunks]
)

# Store in Endee
vectors = [
    {
        "id": chunk["id"],
        "values": embedding,
        "metadata": {
            "document_name": "myfile",
            "content": chunk["content"],
            ...
        }
    }
    for chunk, embedding in zip(chunks, embeddings)
]
endee_client.insert("documents", vectors)
```

### Semantic Search
```python
# Embed query
query_embedding = embedding_service.embed_text("What is AI?")

# Search in Endee
results = endee_client.search(
    index_name="documents",
    query_vector=query_embedding,
    k=5,
    metric="cosine"
)

# Results include similarity scores and metadata
for result in results:
    print(f"Score: {result['score']}")
    print(f"Content: {result['metadata']['content']}")
```

## 📁 Project Structure

```
endee-rag-system/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── endee_client.py         # Endee database client
│   ├── embedding_service.py    # Embeddings & chunking
│   └── rag_service.py          # RAG orchestration
├── scripts/
│   ├── ingest_samples.py       # Sample data ingestion
│   └── example_search.py       # Example queries
├── tests/
│   └── (test files)
├── data/
│   └── (document storage)
├── docs/
│   └── (documentation)
├── .env.example                # Environment template
├── .gitignore
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project metadata
├── tsconfig.json              # TypeScript config (if needed)
└── README.md                  # This file
```

## 🔐 Security Considerations

1. **API Key Management**
   - Never commit `.env` with real API keys
   - Use environment variables in production
   - Rotate keys regularly

2. **Endee Authentication**
   - Use `ENDEE_AUTH_TOKEN` in production
   - Change default tokens

3. **Input Validation**
   - API validates all inputs
   - File uploads are validated
   - Size limits can be configured

4. **CORS Configuration**
   - Currently allows all origins (development)
   - Restrict in production

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**
```bash
export ENVIRONMENT=production
export API_RELOAD=false
export LOG_LEVEL=WARNING
```

2. **Using Gunicorn (Production ASGI Server)**
```bash
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

3. **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "src.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

4. **Kubernetes Deployment**
See `docs/kubernetes.yaml` for example configuration.

## 📈 Performance Optimization

- **Batch Embedding**: Generate embeddings in batches
- **Caching**: Cache frequent query embeddings
- **Chunking Strategy**: Optimize chunk size for your use case
- **Index Metrics**: Choose appropriate distance metric (cosine for normalized embeddings)
- **Endee SIMD**: Use AVX2/AVX512 builds for better performance

## 🐛 Troubleshooting

### Endee Connection Error
```
Error: Endee server is not responding
```
- Verify Endee is running: `curl http://localhost:8080/api/v1/health`
- Check `ENDEE_BASE_URL` in `.env`

### Out of Memory
```
CUDA out of memory / Out of memory errors
```
- Reduce `CHUNK_SIZE` in `.env`
- Batch process documents
- Use CPU-based embeddings instead of GPU

### LLM Errors
```
Error: Failed to generate answer
```
- Verify `OPENAI_API_KEY` is set correctly
- Check API key has sufficient quota
- Verify API key has correct permissions

## 📚 Additional Resources

- [Endee Documentation](https://docs.endee.io)
- [Sentence-Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [RAG Papers](https://arxiv.org/abs/2005.11401)
- [Vector Search Best Practices](https://github.com/qdrant/vector-search-benchmark)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Endee Labs** for the high-performance vector database
- **Hugging Face** for sentence-transformers models
- **OpenAI** for language models
- **FastAPI** community

## 📧 Contact & Support

- GitHub Issues: [Report bugs or request features](https://github.com/your-username/endee-rag-system/issues)
- Discussions: [Ask questions and share ideas](https://github.com/your-username/endee-rag-system/discussions)

---

**Built with ❤️ using Endee - The High-Performance Vector Database**
