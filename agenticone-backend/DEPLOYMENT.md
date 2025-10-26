# AgenticOne Backend Deployment Guide

## Overview

The AgenticOne Backend is a FastAPI-based service that provides AI-powered engineering analysis through specialized agents. This guide covers deployment options and configuration.

## Architecture Components

### Core Services
- **FastAPI Application**: REST API with CORS support
- **AI Agents**: 4 specialized engineering agents
- **RAG Service**: Document processing and retrieval
- **Vector Store**: Embeddings and similarity search
- **Vision Service**: Image analysis with Vertex AI
- **Report Generator**: Comprehensive report creation

### AI Agents
1. **Discipline Head**: Project coordination and decision making
2. **Methods Specialist**: Engineering methods and procedures
3. **Corrosion Engineer**: Corrosion analysis and prevention
4. **Subsea Engineer**: Subsea systems and operations

## Deployment Options

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your configuration

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Docker Deployment

```bash
# Build the image
docker build -t agenticone-backend .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  -e VERTEX_AI_LOCATION=us-central1 \
  agenticone-backend
```

### 3. Google Cloud Run

```bash
# Build and deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy manually
gcloud run deploy agenticone-backend \
  --image gcr.io/PROJECT_ID/agenticone-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10
```

## Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID | `my-project-123` |
| `VERTEX_AI_LOCATION` | Vertex AI region | `us-central1` |
| `VERTEX_AI_MODEL` | Gemini model name | `gemini-1.5-pro` |
| `FIRESTORE_PROJECT_ID` | Firestore project ID | `my-project-123` |
| `CLOUD_STORAGE_BUCKET` | Cloud Storage bucket | `my-storage-bucket` |
| `VECTOR_SEARCH_INDEX_ID` | Vector search index | `my-vector-index` |
| `SECRET_KEY` | Application secret key | `your-secret-key` |

### Google Cloud Setup

1. **Enable APIs**:
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable firestore.googleapis.com
   gcloud services enable storage.googleapis.com
   gcloud services enable run.googleapis.com
   ```

2. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create agenticone-backend \
     --display-name="AgenticOne Backend Service Account"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:agenticone-backend@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:agenticone-backend@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/datastore.user"
   
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member="serviceAccount:agenticone-backend@PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

3. **Create and Download Key**:
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=agenticone-backend@PROJECT_ID.iam.gserviceaccount.com
   ```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Document Upload
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "metadata={\"type\": \"technical_document\"}"
```

### Document Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc-123",
    "analysis_type": "comprehensive_analysis",
    "agent_type": "discipline_head"
  }'
```

### Report Generation
```bash
curl -X POST "http://localhost:8000/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_ids": ["analysis-1", "analysis-2"],
    "report_type": "technical_report"
  }'
```

## Monitoring and Logging

### Health Checks
- `GET /health` - Service health status
- `GET /` - Basic health check

### Logging
- Structured logging with timestamps
- Error tracking and monitoring
- Performance metrics

### Metrics
- Request count and latency
- Agent performance metrics
- Document processing statistics

## Security Considerations

### CORS Configuration
```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173", 
    "https://agenticone.vercel.app"
]
```

### Authentication
- Service account authentication for Google Cloud
- API key management
- Request validation and sanitization

### Data Protection
- Secure document processing
- Encrypted storage
- Access control and permissions

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Authentication Errors**: Check service account permissions
   ```bash
   gcloud auth application-default login
   ```

3. **Memory Issues**: Increase Cloud Run memory allocation
   ```bash
   gcloud run services update agenticone-backend \
     --memory 4Gi
   ```

4. **Timeout Issues**: Increase timeout settings
   ```bash
   gcloud run services update agenticone-backend \
     --timeout 900
   ```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with debug mode
uvicorn app.main:app --reload --log-level debug
```

## Performance Optimization

### Resource Allocation
- **CPU**: 2-4 cores recommended
- **Memory**: 2-4GB for production
- **Storage**: SSD recommended

### Scaling
- **Min Instances**: 1 (for faster cold starts)
- **Max Instances**: 10-100 (based on load)
- **Concurrency**: 100-1000 requests per instance

### Caching
- Vector embeddings caching
- Document processing results
- Agent response caching

## Backup and Recovery

### Data Backup
- Firestore automatic backups
- Cloud Storage versioning
- Configuration backups

### Disaster Recovery
- Multi-region deployment
- Data replication
- Service redundancy

## Cost Optimization

### Resource Management
- Right-size instances
- Use preemptible instances for non-critical workloads
- Implement request queuing

### Monitoring Costs
- Set up billing alerts
- Monitor resource usage
- Optimize API calls

## Support and Maintenance

### Regular Updates
- Dependency updates
- Security patches
- Feature enhancements

### Monitoring
- Health check endpoints
- Performance metrics
- Error tracking

### Documentation
- API documentation
- Deployment guides
- Troubleshooting guides
