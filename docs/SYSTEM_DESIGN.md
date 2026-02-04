# System Design

Detailed technical design of the Endee RAG System.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│  (Web UI, CLI, Mobile, Third-party Services)            │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTP/REST
        ┌────────────▼────────────┐
        │   FastAPI Application   │
        │  (/api/v1/*)            │
        │  - Request validation   │
        │  - Routing              │
        │  - Response formatting  │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────────────┐
        │     RAG Service Layer           │
        │  - Orchestration                │
        │  - Business logic               │
        │  - Error handling               │
        └────────────┬────────────────────┘
                     │
        ┌────────────▼──────────┬─────────────┐
        │                       │             │
        │   EmbeddingService    │  EndeeClient│
        │  (sentence-trans)     │   (REST)    │
        │  - Text embedding     │   - Search  │
        │  - Chunking           │   - Insert  │
        │  - Preprocessing      │   - Index   │
        │                       │             │
        └───────────┬───────────┴──────┬──────┘
                    │                  │
        ┌───────────▼──────────┐  ┌────▼──────────┐
        │  Transformer Model   │  │   Endee DB    │
        │  (all-MiniLM-L6-v2)  │  │  - Vectors    │
        │  - Dimensions: 384   │  │  - Indices    │
        │  - Pool: mean tokens │  │  - Search ops │
        └──────────────────────┘  └───────────────┘

        Optional:
        ┌──────────────────────────┐
        │   OpenAI API             │
        │  (LLM for answers)       │
        └──────────────────────────┘
```

## Core Components

### 1. FastAPI Application (`src/main.py`)

**Responsibilities:**
- HTTP request handling and routing
- Input validation using Pydantic models
- Response serialization
- CORS and security headers
- Lifespan management (startup/shutdown)

**Key Features:**
- Auto-generated OpenAPI documentation
- Request/response validation
- Async support for non-blocking I/O
- CORS middleware for cross-origin requests

### 2. RAG Service (`src/rag_service.py`)

**Responsibilities:**
- Orchestrate document ingestion pipeline
- Coordinate semantic search operations
- Integrate with LLM for answer generation
- Error handling and logging

**Key Methods:**
```python
initialize()          # Setup Endee connection
ingest_document()     # Add document to system
search()             # Semantic search
_generate_answer()   # LLM-based answer generation
get_statistics()     # System metrics
```

### 3. Embedding Service (`src/embedding_service.py`)

**Responsibilities:**
- Generate text embeddings using sentence-transformers
- Split documents into semantic chunks
- Manage embedding model lifecycle

**Key Methods:**
```python
embed_text()         # Single text embedding
embed_texts()        # Batch embedding
chunk_document()     # Document chunking
```

**Model:** `all-MiniLM-L6-v2`
- Output dimension: 384
- Optimized for semantic similarity
- Fast inference on CPU/GPU
- 22M parameters

### 4. Endee Client (`src/endee_client.py`)

**Responsibilities:**
- HTTP communication with Endee server
- Index management (create, delete, list)
- Vector operations (insert, search, delete)
- Health monitoring

**Key Methods:**
```python
create_index()       # Create vector index
insert()            # Store vectors
search()            # Semantic search
health_check()      # Server health
```

### 5. Configuration (`src/config.py`)

**Responsibilities:**
- Environment variable loading
- Setting validation
- Configuration management

**Key Settings:**
```python
ENDEE_BASE_URL      # Endee server location
EMBEDDING_MODEL     # Model to use
CHUNK_SIZE          # Document chunk size
OPENAI_API_KEY      # LLM configuration
```

## Data Flow

### Document Ingestion Flow

```
User Document
      │
      ▼
┌─────────────────┐
│ Split into      │  Chunk: 512 chars
│ Overlapping     │  Overlap: 50 chars
│ Chunks          │
└────────┬────────┘
         │
      Chunks: [
         {"id": "uuid1", "content": "...", "metadata": {...}},
         {"id": "uuid2", "content": "...", "metadata": {...}},
         ...
      ]
      │
      ▼
┌──────────────────────┐
│ Generate Embeddings  │
│ using Sentence-      │
│ Transformers         │
└────────┬─────────────┘
         │
      Embeddings: [
         [0.124, 0.087, ..., 0.045],  // 384-dim vector
         [0.098, 0.112, ..., 0.156],
         ...
      ]
      │
      ▼
┌──────────────────────┐
│ Create Vectors with  │
│ Metadata             │
└────────┬─────────────┘
         │
      Vectors: [
         {
           "id": "uuid1",
           "values": [0.124, ...],
           "metadata": {
              "document_name": "...",
              "chunk_index": 0,
              "content": "...",
              ...
           }
         },
         ...
      ]
      │
      ▼
┌──────────────────────┐
│ Insert into Endee    │
│ Vector Database      │
└──────────────────────┘
      │
      ▼
Stored in Endee with
index "documents"
```

### Search Flow

```
User Query
      │
      ▼
┌──────────────────────┐
│ Generate Query       │
│ Embedding            │
└────────┬─────────────┘
         │
      Query Vector: [0.156, 0.089, ..., 0.078]
      │
      ▼
┌──────────────────────┐
│ Search in Endee      │
│ using Cosine Metric  │  k=5 (top 5)
└────────┬─────────────┘
         │
      Results: [
         {
            "id": "uuid1",
            "score": 0.892,
            "metadata": {...}
         },
         ...
      ]
      │
      ▼
┌──────────────────────┐
│ Optional: LLM Answer │
│ Generation           │
└────────┬─────────────┘
         │
         ├─ Extract context from results
         ├─ Call OpenAI API
         └─ Generate answer
         │
      Generated Answer:
      "Python is a high-level programming..."
      │
      ▼
Return to User
(results + optional answer)
```

## Endee Integration

### Index Schema

**Index Name:** `documents`

**Configuration:**
- **Dimension:** 384 (from all-MiniLM-L6-v2)
- **Metric:** cosine
- **Vector Type:** float32

### Vector Structure

```json
{
  "id": "chunk-uuid",
  "values": [0.124, 0.087, ..., 0.045],
  "metadata": {
    "document_name": "Python Guide",
    "chunk_index": 0,
    "original_length": 5000,
    "start_pos": 0,
    "end_pos": 512,
    "content": "Python is a high-level...",
    "source_url": "https://example.com"
  }
}
```

### API Calls to Endee

**Create Index:**
```
POST /api/v1/index/create
{
  "name": "documents",
  "dimension": 384,
  "metric": "cosine"
}
```

**Insert Vectors:**
```
POST /api/v1/index/documents/insert
{
  "vectors": [
    {
      "id": "...",
      "values": [...],
      "metadata": {...}
    }
  ]
}
```

**Search:**
```
POST /api/v1/index/documents/search
{
  "query": [0.124, 0.087, ...],
  "k": 5,
  "filter": {...}  // optional
}
```

## Performance Characteristics

### Embedding Generation
- **Model:** all-MiniLM-L6-v2
- **Latency:** ~5-10ms per text (CPU)
- **Throughput:** 100+ texts/second (batch)
- **Memory:** ~350MB for model

### Vector Search
- **Latency:** ~10-50ms for 10K vectors (Endee optimized)
- **Throughput:** 100+ queries/second
- **Memory:** ~1.5MB per 10K 384-dim vectors

### End-to-End
- **Ingestion:** 500 documents (2500 chunks) in ~2 minutes
- **Search:** Average 45ms retrieval + 50ms embedding = 95ms baseline
- **With LLM:** +1-2 seconds for OpenAI API call

### Scalability

| Documents | Chunks | Vectors | Memory | Ingestion | Search |
|-----------|--------|---------|--------|-----------|--------|
| 100       | 500    | 500     | ~1MB   | 5s        | 50ms   |
| 1K        | 5K     | 5K      | ~8MB   | 30s       | 60ms   |
| 10K       | 50K    | 50K     | ~75MB  | 3min      | 80ms   |
| 100K      | 500K   | 500K    | ~750MB | 30min     | 150ms  |
| 1M        | 5M     | 5M      | ~7.5GB | 5hours    | 200ms  |

## Error Handling Strategy

### Error Hierarchy

```
Exception
├── EndeeError
│   ├── ConnectionError
│   ├── IndexError
│   └── SearchError
├── EmbeddingError
│   ├── ModelLoadError
│   └── ProcessingError
├── RAGError
│   ├── IngestionError
│   └── SearchError
└── APIError
    ├── ValidationError
    └── ServerError
```

### Recovery Strategies

**Endee Connection Failure:**
1. Retry with exponential backoff
2. Log error for monitoring
3. Return 503 Service Unavailable

**LLM Integration Failure:**
1. Return search results without answer
2. Log warning
3. Continue normal operation

**Embedding Generation Failure:**
1. Log and skip chunk
2. Continue with other chunks
3. Return partial results

## Security Considerations

### Current Implementation

- No authentication (development)
- CORS allows all origins
- Input validation with Pydantic
- File upload validation

### Production Recommendations

1. **API Authentication**
   - Implement API key validation
   - Use JWT tokens
   - Rate limiting per API key

2. **Endee Security**
   - Set `ENDEE_AUTH_TOKEN` environment variable
   - Restrict network access
   - Use HTTPS/TLS

3. **Data Security**
   - Encrypt sensitive metadata
   - Implement access control
   - Audit logging

4. **Input Validation**
   - File size limits
   - Content type validation
   - SQL injection prevention (if using DB)

## Deployment Architectures

### Single Node
```
Client → API (8000) → Endee (8080)
```

### Load Balanced
```
Client → Load Balancer
         ├→ API Instance 1 (8001)
         ├→ API Instance 2 (8002)
         └→ API Instance 3 (8003)
              └→ Endee (8080)
```

### Kubernetes
```
Client → Ingress
         ├→ API Pod (replica 3)
         │   └→ Endee StatefulSet (replica 1)
         └→ Persistent Volume
```

## Monitoring & Observability

### Metrics to Track

- **Latency:** API response time, search time
- **Throughput:** Requests/sec, vectors inserted/sec
- **Error Rate:** Failed ingestions, failed searches
- **Resource Usage:** CPU, memory, disk I/O
- **Cache Hit Rate:** If caching implemented

### Logging

- All API requests logged
- Document ingestion events
- Search queries and results
- Error stack traces

### Health Checks

```
GET /health
└─ Checks:
   - API running
   - Endee connected
   - Index accessible
```

## Future Enhancements

1. **Advanced Features**
   - Hybrid search (keyword + semantic)
   - Multi-modal embeddings (text + image)
   - Real-time document updates
   - WebSocket streaming

2. **Performance**
   - Embedding caching
   - Query result caching
   - Batch processing optimization
   - SIMD optimizations

3. **Capabilities**
   - Multiple indices
   - Metadata filtering
   - Document versioning
   - Change tracking

4. **Integration**
   - Database connectors
   - Cloud storage integration
   - Message queue support
   - Webhook callbacks
