# Deployment Guide

Production deployment guide for the Endee RAG System.

## Deployment Options

### Option 1: Docker Compose (Simple)

Best for: Single server, development/staging

**Steps:**

1. Clone repository:
```bash
git clone https://github.com/your-username/endee-rag-system.git
cd endee-rag-system
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with production values
```

3. Start services:
```bash
docker-compose up -d
```

4. Verify:
```bash
curl http://localhost:8080/api/v1/health  # Endee
curl http://localhost:8000/health          # API
```

5. Ingest data:
```bash
docker exec -it endee-rag-api python -m scripts.ingest_samples
```

### Option 2: Kubernetes (Advanced)

Best for: Production, high availability, auto-scaling

**Prerequisites:**
- Kubernetes cluster (1.24+)
- kubectl configured
- Helm 3+ (optional)

**Steps:**

1. Create namespace:
```bash
kubectl create namespace endee
```

2. Create ConfigMap for settings:
```bash
kubectl create configmap endee-config \
  --from-env-file=.env \
  -n endee
```

3. Deploy Endee:
```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: endee-server
  namespace: endee
spec:
  serviceName: endee
  replicas: 1
  selector:
    matchLabels:
      app: endee
  template:
    metadata:
      labels:
        app: endee
    spec:
      containers:
      - name: endee
        image: endeeio/endee-server:latest
        ports:
        - containerPort: 8080
        env:
        - name: NDD_NUM_THREADS
          value: "0"
        - name: NDD_AUTH_TOKEN
          valueFrom:
            configMapKeyRef:
              name: endee-config
              key: ENDEE_AUTH_TOKEN
        volumeMounts:
        - name: data
          mountPath: /data
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "8Gi"
            cpu: "4"
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
---
apiVersion: v1
kind: Service
metadata:
  name: endee-service
  namespace: endee
spec:
  clusterIP: None
  selector:
    app: endee
  ports:
  - port: 8080
    targetPort: 8080
EOF
```

4. Deploy API:
```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: endee-rag-api
  namespace: endee
spec:
  replicas: 3
  selector:
    matchLabels:
      app: endee-rag-api
  template:
    metadata:
      labels:
        app: endee-rag-api
    spec:
      containers:
      - name: api
        image: your-registry/endee-rag-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENDEE_BASE_URL
          value: http://endee-service:8080
        envFrom:
        - configMapRef:
            name: endee-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api-service
  namespace: endee
spec:
  type: LoadBalancer
  selector:
    app: endee-rag-api
  ports:
  - port: 80
    targetPort: 8000
EOF
```

5. Check deployment:
```bash
kubectl get pods -n endee
kubectl logs -n endee deployment/endee-rag-api
```

### Option 3: AWS ECS (Container Orchestration)

Best for: AWS-native deployments

**Steps:**

1. Create ECR repository:
```bash
aws ecr create-repository --repository-name endee-rag-api --region us-east-1
```

2. Build and push image:
```bash
docker build -t endee-rag-api:latest .
docker tag endee-rag-api:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/endee-rag-api:latest
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/endee-rag-api:latest
```

3. Create ECS task definitions and services
4. Configure load balancer
5. Set up CloudWatch monitoring

## Environment Configuration

### Development
```env
ENVIRONMENT=development
API_RELOAD=true
LOG_LEVEL=DEBUG
ENDEE_BASE_URL=http://localhost:8080
```

### Staging
```env
ENVIRONMENT=staging
API_RELOAD=false
LOG_LEVEL=INFO
ENDEE_BASE_URL=https://endee-staging.example.com
ENDEE_AUTH_TOKEN=<secure-token>
```

### Production
```env
ENVIRONMENT=production
API_RELOAD=false
LOG_LEVEL=WARNING
ENDEE_BASE_URL=https://endee-prod.example.com
ENDEE_AUTH_TOKEN=<secure-token>
OPENAI_API_KEY=<encrypted-key>
```

## Scaling Strategies

### Horizontal Scaling (API Instances)

```
Load Balancer
    ├─ API Instance 1
    ├─ API Instance 2
    ├─ API Instance 3
    └─ (Can scale to N instances)
         └─ Endee Database (shared)
```

**Benefits:**
- Handle more concurrent requests
- Distribute load
- Zero-downtime deployments

**Implementation:**
```bash
# Docker Compose
docker-compose up --scale api=5

# Kubernetes
kubectl scale deployment endee-rag-api --replicas=5
```

### Vertical Scaling (Endee Database)

```
Multiple API Instances
    └─ Endee with more resources
         - More RAM
         - More CPU cores
         - Faster storage
```

**Benefits:**
- Faster search operations
- Handle larger vector indices
- Better embedding generation

### Caching Layer

```
API Instances
    └─ Redis Cache
         └─ Endee Database
```

**Cached Items:**
- Embedding results (query → vector)
- Search results (query → results)
- Model weights

## Monitoring & Alerts

### Prometheus Metrics

Add to `src/main.py`:
```python
from prometheus_client import Counter, Histogram, Gauge
from fastapi_prometheus_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Custom metrics
search_count = Counter('search_total', 'Total searches')
search_duration = Histogram('search_duration_seconds', 'Search time')
index_size = Gauge('index_size_vectors', 'Vectors in index')
```

### Alert Rules

```yaml
- alert: APIHighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  annotations:
    summary: "High error rate detected"

- alert: EndeeDown
  expr: up{job="endee"} == 0
  for: 1m
  annotations:
    summary: "Endee server is down"

- alert: APIHighLatency
  expr: histogram_quantile(0.95, api_request_duration) > 2
  for: 5m
  annotations:
    summary: "API response time is high"
```

## Backup & Recovery

### Backup Strategy

**Backup Endee Data:**
```bash
# Docker
docker exec endee-server tar czf /data/backup.tar.gz /data/

# Kubernetes
kubectl exec -it endee-server-0 -- tar czf /backup.tar.gz /data/
```

**Backup Frequency:**
- Daily snapshots
- Weekly full backups
- Monthly archives

### Recovery

```bash
# Restore from backup
docker exec endee-server tar xzf /backup/backup.tar.gz -C /data/
docker restart endee-server
```

## SSL/TLS Configuration

### Using Nginx Reverse Proxy

```nginx
upstream endee_api {
    server localhost:8000;
}

server {
    listen 443 ssl;
    server_name endee.example.com;

    ssl_certificate /etc/letsencrypt/live/endee.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/endee.example.com/privkey.pem;

    location / {
        proxy_pass http://endee_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name endee.example.com;
    redirect 301 https://endee.example.com$request_uri;
}
```

### Using Let's Encrypt

```bash
certbot certonly --standalone -d endee.example.com
certbot renew --quiet --no-eff-email
```

## Troubleshooting

### Issue: API can't connect to Endee

**Debug:**
```bash
# Check Endee is running
curl http://endee-host:8080/api/v1/health

# Check network connectivity
ping endee-host

# Check logs
docker logs endee-server
docker logs endee-rag-api
```

**Solution:**
- Verify `ENDEE_BASE_URL` is correct
- Check firewall rules
- Verify Endee is running
- Check auth token if using authentication

### Issue: High memory usage

**Debug:**
```bash
# Monitor memory
docker stats endee-rag-api

# Check process
ps aux | grep python
```

**Solutions:**
- Reduce `CHUNK_SIZE`
- Batch process documents
- Increase container memory limit
- Use smaller embedding model

### Issue: Slow search performance

**Debug:**
```python
# Run benchmark
python -m scripts.benchmark_search

# Check index stats
curl http://localhost:8000/api/v1/statistics
```

**Solutions:**
- Check Endee SIMD configuration (AVX2/AVX512)
- Increase Endee thread count
- Optimize chunk size
- Add caching layer

## Performance Tuning

### API Tuning

```python
# src/main.py
app = FastAPI(
    # Enable async features
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Uvicorn workers
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.main:app
```

### Endee Tuning

```bash
# Run.sh parameters
NDD_NUM_THREADS=8      # Set to CPU count
NDD_DATA_DIR=/data
NDD_CACHE_SIZE=1000    # Adjust for memory
```

### Model Tuning

```python
# Batch processing
embeddings = embedding_service.embed_texts(
    texts,
    batch_size=32,  # Adjust based on memory
    show_progress_bar=False
)
```

## Cost Optimization

1. **Use Spot Instances** (AWS EC2, GCP Compute)
   - 70% cheaper than on-demand
   - Good for stateless API servers

2. **Vertical Pod Autoscaling** (Kubernetes)
   - Automatically adjust resource requests

3. **Reserved Instances**
   - For baseline load (Endee)
   - 30-50% discount

4. **Caching Strategy**
   - Reduce API calls to LLM
   - Cache frequent embeddings

## Post-Deployment Checklist

- [ ] API responds to requests
- [ ] Endee health check passes
- [ ] Sample data ingested successfully
- [ ] Search queries return results
- [ ] LLM integration working (if configured)
- [ ] Monitoring/logging enabled
- [ ] Backup strategy implemented
- [ ] SSL/TLS configured
- [ ] API documentation accessible
- [ ] Load testing passed
- [ ] Disaster recovery tested
- [ ] Capacity planning reviewed

## Support & Debugging

- Check logs: `kubectl logs -n endee deployment/endee-rag-api`
- API docs: `https://endee.example.com/docs`
- Health endpoint: `https://endee.example.com/health`
- Metrics: `https://endee.example.com/metrics` (if Prometheus enabled)
