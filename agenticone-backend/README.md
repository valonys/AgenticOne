# AgenticOne Backend

A FastAPI-based backend service for the AgenticOne AI-powered engineering analysis platform. This service provides specialized AI agents for engineering analysis, document processing, and report generation.

## Architecture

The backend follows a microservices architecture with the following components:

- **FastAPI Application**: Main web framework with REST API endpoints
- **AI Agents**: Specialized agents for different engineering disciplines
- **RAG Service**: Retrieval-Augmented Generation for document processing
- **Vector Store**: Document embeddings and similarity search
- **Vision Service**: Image analysis using Vertex AI Gemini
- **Report Generator**: Comprehensive analysis report generation
- **Firestore Database**: Metadata storage and document management

## Features

### AI Agents
- **Discipline Head**: Overall project coordination and decision making
- **Methods Specialist**: Engineering methods and procedures analysis
- **Corrosion Engineer**: Corrosion analysis and prevention strategies
- **Subsea Engineer**: Subsea systems and underwater operations

### Document Processing
- PDF, image, and text document processing
- Text extraction and content analysis
- Image analysis and object detection
- Technical diagram interpretation

### Analysis Capabilities
- Multi-modal document analysis
- Risk assessment and compliance review
- Technical specification extraction
- Quality assurance evaluation

### Report Generation
- Executive summaries
- Technical analysis reports
- Recommendations and action items
- Custom report templates

## API Endpoints

### Core Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /agents` - List available agents

### Analysis Endpoints
- `POST /analyze` - Analyze document with specified agent
- `POST /upload` - Upload and process document
- `POST /generate-report` - Generate comprehensive report

## Installation

### Prerequisites
- Python 3.11+
- Google Cloud Project with Vertex AI, Firestore, and Cloud Storage enabled
- Docker (for containerized deployment)

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd agenticone-backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t agenticone-backend .
```

2. Run the container:
```bash
docker run -p 8000:8000 agenticone-backend
```

### Google Cloud Run Deployment

1. Set up Google Cloud Build:
```bash
gcloud builds submit --config cloudbuild.yaml
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy agenticone-backend \
  --image gcr.io/PROJECT_ID/agenticone-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID | Required |
| `VERTEX_AI_LOCATION` | Vertex AI region | `us-central1` |
| `VERTEX_AI_MODEL` | Gemini model name | `gemini-1.5-pro` |
| `FIRESTORE_PROJECT_ID` | Firestore project ID | Required |
| `CLOUD_STORAGE_BUCKET` | Cloud Storage bucket | Required |
| `VECTOR_SEARCH_INDEX_ID` | Vector search index | Required |
| `SECRET_KEY` | Application secret key | Required |

### Google Cloud Setup

1. Enable required APIs:
   - Vertex AI API
   - Firestore API
   - Cloud Storage API
   - Cloud Run API

2. Create service account with required permissions:
   - Vertex AI User
   - Firestore User
   - Storage Admin
   - Cloud Run Admin

3. Set up authentication:
```bash
gcloud auth application-default login
```

## Usage

### Document Analysis

```python
import requests

# Upload document
response = requests.post(
    "http://localhost:8000/upload",
    files={"file": open("document.pdf", "rb")},
    data={"metadata": '{"type": "technical_document"}'}
)

# Analyze document
analysis_response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "document_id": response.json()["document_id"],
        "analysis_type": "comprehensive_analysis",
        "agent_type": "discipline_head"
    }
)
```

### Report Generation

```python
# Generate report
report_response = requests.post(
    "http://localhost:8000/generate-report",
    json={
        "analysis_ids": ["analysis_1", "analysis_2"],
        "report_type": "technical_report"
    }
)
```

## Development

### Code Structure

```
app/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── agents/                # AI agents
│   ├── base_agent.py      # Base agent class
│   ├── discipline_head.py # Discipline Head agent
│   ├── methods_specialist.py
│   ├── corrosion_engineer.py
│   └── subsea_engineer.py
├── services/              # Core services
│   ├── rag_service.py     # RAG implementation
│   ├── vector_store.py    # Vector database
│   ├── document_processor.py
│   ├── vision_service.py  # Image analysis
│   └── report_generator.py
├── models/                # Data models
│   ├── schemas.py         # Pydantic schemas
│   └── database.py       # Firestore models
└── utils/                 # Utilities
    ├── prompts.py         # AI prompts
    └── helpers.py         # Helper functions
```

### Testing

Run tests with pytest:
```bash
pytest tests/
```

### Code Quality

Format code with black:
```bash
black app/
```

Sort imports with isort:
```bash
isort app/
```

Lint with flake8:
```bash
flake8 app/
```

Type checking with mypy:
```bash
mypy app/
```

## Monitoring

The application includes health checks and monitoring endpoints:

- `GET /health` - Service health status
- Prometheus metrics (if enabled)
- Structured logging with timestamps

## Security

- CORS configuration for frontend integration
- Environment variable management
- Secure document processing
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation for common issues
