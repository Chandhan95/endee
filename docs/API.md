# API Reference

Complete API documentation for the Endee RAG System.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API is open (no authentication required). For production, implement API key authentication.

## Content Types

All endpoints except file upload use JSON:
- Request: `Content-Type: application/json`
- Response: `application/json`

File upload endpoint uses:
- Request: `Content-Type: multipart/form-data`

## Response Format

All responses follow a standard format:

**Success (200-201):**
```json
{
  "data": { ... }
}
```

**Error (4xx-5xx):**
```json
{
  "detail": "Error message"
}
```

---

## Endpoints

### 1. Health Check

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "rag_initialized": true,
  "endee_connected": true
}
```

**Status Codes:**
- `200`: Healthy
- `503`: Service Unavailable

---

### 2. Ingest Document (Form Data)

**Request:**
```http
POST /api/v1/ingest
Content-Type: multipart/form-data

document_name=My+Document
content=This+is+the+document+content
source_url=https://example.com
```

**Parameters:**
- `document_name` (string, required): Unique document identifier
- `content` (string, required): Document text content
- `source_url` (string, optional): Source URL of the document

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "document_name=tutorial" \
  -F "content=Python is awesome" \
  -F "source_url=https://example.com"
```

**Response (201 Created):**
```json
{
  "document_name": "tutorial",
  "chunks_added": 1,
  "total_content_length": 20
}
```

**Error Responses:**
- `400`: Missing required fields
- `500`: Server error

---

### 3. Ingest File

**Request:**
```http
POST /api/v1/ingest-file
Content-Type: multipart/form-data

file=<binary>
source_url=https://example.com
```

**Parameters:**
- `file` (file, required): Text file (.txt, .md, etc.)
- `source_url` (string, optional): Source URL

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/ingest-file" \
  -F "file=@mydocument.txt"
```

**Response (201 Created):**
```json
{
  "document_name": "mydocument.txt",
  "chunks_added": 5,
  "total_content_length": 2500
}
```

**Error Responses:**
- `400`: Invalid file format or missing file
- `500`: Server error during processing

---

### 4. Search Documents

**Request:**
```http
POST /api/v1/search
Content-Type: application/json

{
  "query": "What is machine learning?",
  "top_k": 5,
  "use_llm": false
}
```

**Request Body:**
- `query` (string, required): Search query
- `top_k` (integer, optional): Number of results to return. Default: 5, Max: 100
- `use_llm` (boolean, optional): Generate LLM answer. Default: false

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Python?",
    "top_k": 3,
    "use_llm": false
  }'
```

**Response (200 OK):**
```json
{
  "query": "What is Python?",
  "results": [
    {
      "id": "chunk-uuid-1",
      "score": 0.892,
      "metadata": {
        "document_name": "Python Guide",
        "chunk_index": 0,
        "content": "Python is a high-level programming language...",
        "source_url": null,
        "original_length": 5000
      }
    },
    {
      "id": "chunk-uuid-2",
      "score": 0.756,
      "metadata": { ... }
    }
  ],
  "generated_answer": null,
  "retrieval_time_ms": 45.23,
  "total_time_ms": 89.15,
  "result_count": 2
}
```

**With LLM Response:**
```json
{
  "query": "What is Python used for?",
  "results": [...],
  "generated_answer": "Python is widely used for web development, data analysis, machine learning, scientific computing, and automation...",
  "retrieval_time_ms": 45.23,
  "total_time_ms": 2450.15,
  "result_count": 3
}
```

**Response Fields:**
- `query`: Echo of the search query
- `results`: Array of matched documents
  - `id`: Vector ID
  - `score`: Similarity score (0-1, higher is better)
  - `metadata`: Document metadata
- `generated_answer`: LLM-generated answer (null if `use_llm` is false)
- `retrieval_time_ms`: Time to retrieve results
- `total_time_ms`: Total request time
- `result_count`: Number of results returned

**Status Codes:**
- `200`: Success
- `400`: Invalid query
- `503`: Service not available

---

### 5. Get Statistics

**Request:**
```http
GET /api/v1/statistics
```

**Example cURL:**
```bash
curl "http://localhost:8000/api/v1/statistics"
```

**Response (200 OK):**
```json
{
  "index_name": "documents",
  "vector_count": 42,
  "dimension": 384,
  "metric": "cosine"
}
```

**Response Fields:**
- `index_name`: Name of the vector index
- `vector_count`: Total vectors stored
- `dimension`: Embedding dimension
- `metric`: Distance metric used

---

### 6. List Indices

**Request:**
```http
GET /api/v1/indices
```

**Example cURL:**
```bash
curl "http://localhost:8000/api/v1/indices"
```

**Response (200 OK):**
```json
{
  "indices": ["documents", "additional_index"],
  "count": 2
}
```

**Response Fields:**
- `indices`: List of index names
- `count`: Number of indices

---

### 7. Root Endpoint

**Request:**
```http
GET /
```

**Response (200 OK):**
```json
{
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
```

---

## Error Handling

### Common Error Responses

**400 - Bad Request**
```json
{
  "detail": "query is required"
}
```

**503 - Service Unavailable**
```json
{
  "detail": "RAG service not initialized"
}
```

**500 - Internal Server Error**
```json
{
  "detail": "Error ingesting document: connection refused"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, implement:
- Per-IP rate limits
- Per-API-key rate limits
- Request queuing

---

## Performance Tips

1. **Batch Ingestion**: Ingest documents in batches rather than one at a time
2. **Chunk Size**: Adjust `CHUNK_SIZE` based on your documents
   - Smaller chunks (256): Better for questions on specific details
   - Larger chunks (1024): Better for general understanding
3. **Top K Results**: Use appropriate `top_k` value
   - 3-5: Quick searches
   - 10-20: Comprehensive answers
4. **Caching**: Cache frequent query embeddings
5. **Parallel Requests**: The API supports concurrent requests

---

## Integration Examples

### Python
```python
import requests

# Search documents
response = requests.post(
    "http://localhost:8000/api/v1/search",
    json={
        "query": "What is Python?",
        "top_k": 5,
        "use_llm": False
    }
)
results = response.json()
print(results["results"])
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:8000/api/v1/search', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is Python?',
    top_k: 5,
    use_llm: false
  })
});
const results = await response.json();
console.log(results.results);
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "top_k": 5, "use_llm": false}'
```

---

## WebSocket Support (Future)

For real-time streaming responses, WebSocket support will be added in future versions.

---

## Versioning

Current API version: `v1` (in endpoints: `/api/v1/...`)

Future versions will maintain backward compatibility where possible.

---

## Feedback & Support

Report issues or suggest improvements: [GitHub Issues](https://github.com/your-username/endee-rag-system/issues)
