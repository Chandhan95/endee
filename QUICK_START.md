# Quick Start Guide

Get up and running with the Endee RAG System in 5 minutes!

## Step 1: Start Endee Vector Database

### Option A: Using Docker (Recommended)

```bash
docker run -p 8080:8080 -v endee-data:/data endeeio/endee-server:latest
```

Verify it's running:
```bash
curl http://localhost:8080/api/v1/health
```

### Option B: Using Docker Compose (with API)

```bash
docker-compose up
```

This starts both Endee and the RAG API.

## Step 2: Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env if you want to customize settings
# (defaults work fine for local development)
```

## Step 4: Ingest Sample Documents

```bash
python -m scripts.ingest_samples
```

This loads sample documents about Python, Vector Databases, and RAG.

## Step 5: Start the API Server

```bash
python -m uvicorn src.main:app --reload
```

The API is now running at `http://localhost:8000`

## Step 6: Try It Out!

### Open Interactive Docs
Visit: http://localhost:8000/docs

You can test all endpoints directly in the browser!

### Quick Search via cURL

```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Python?", "top_k": 3}'
```

### Ingest Your Own Document

```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "document_name=My Document" \
  -F "content=This is my document content"
```

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/v1/ingest` | Add document (form data) |
| POST | `/api/v1/ingest-file` | Add document (file upload) |
| POST | `/api/v1/search` | Search documents |
| GET | `/api/v1/statistics` | System statistics |
| GET | `/api/v1/indices` | List indices |

## Example: Complete Workflow

```bash
# 1. Check API is running
curl http://localhost:8000/health

# 2. Ingest a document
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "document_name=tutorial" \
  -F "content=Python is a programming language. It is known for its simplicity and readability."

# 3. Search for something
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "What programming language is simple?", "top_k": 5}'

# 4. Get system statistics
curl http://localhost:8000/api/v1/statistics

# 5. List indices
curl http://localhost:8000/api/v1/indices
```

## Enable LLM Answers (Optional)

To get AI-generated answers in addition to search results:

1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```
3. Search with `use_llm: true`:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "What is Python used for?", "use_llm": true}'
   ```

## Troubleshooting

### "Connection refused" to Endee
- Make sure Endee is running: `docker ps`
- Check Endee port is 8080
- Try: `curl http://localhost:8080/api/v1/health`

### ModuleNotFoundError
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

### Port already in use
- Change API port in `.env`: `API_PORT=8001`
- Or kill process: `lsof -i :8000` then `kill -9 <pid>`

## Next Steps

- Read the [full README](README.md) for detailed documentation
- Check [API docs](API.md) for all endpoints
- Run example search: `python -m scripts.example_search`
- Customize chunking strategy for your documents
- Deploy using Docker or Kubernetes

## Need Help?

- Check logs: `python -m scripts.example_search` to see what's happening
- Review `.env.example` for all configuration options
- Visit Endee docs: https://docs.endee.io
