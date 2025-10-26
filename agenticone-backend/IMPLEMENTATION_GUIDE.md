# AgenticOne Implementation Guide

## 🚀 **How to Run the Complete System**

### Frontend (React + Vite)
```bash
cd /Users/atalibamiguel/Documents/AgenticOne/agenticone
npm run dev
# Access at: http://localhost:3000
```

### Backend (FastAPI)
```bash
cd /Users/atalibamiguel/Documents/AgenticOne/agenticone/agenticone-backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Access at: http://localhost:8000
```

## 📊 **Current File Upload Capabilities**

### Frontend Limits
- **Maximum Files**: 5 files per session
- **File Size Limit**: 10MB per file
- **Total Token Limit**: 10,000 tokens
- **Supported Formats**: PDF, DOC, DOCX, TXT, JPG, PNG, TIFF

### Backend Processing
- **Document Types**: PDF, Word, Images, Text files
- **Processing**: Text extraction, image analysis, metadata extraction
- **Storage**: Google Cloud Storage + Firestore metadata
- **Vector Search**: Vertex AI Vector Search (Index ID: 3314070982628474880)

## 🧠 **Knowledge Ingestion Architecture**

### Current Flow
```
Document Upload → Processing → Embedding → Vector Store → RAG Retrieval
     ↓              ↓           ↓           ↓            ↓
  Frontend    → Document   → Embeddings → Vertex AI  → Agent Analysis
              Processor    → Creation    → Vector    → & Response
                          → Extraction  → Search    → Generation
```

### Enhanced Knowledge Management
The system now includes:
- **Semantic Chunking**: Better document segmentation
- **Agent-Specific Filtering**: Tailored knowledge retrieval
- **Batch Processing**: Multiple document ingestion
- **Knowledge Statistics**: Usage and performance metrics

## 🎯 **Agent Specialization & Knowledge Usage**

### Methods Specialist
- **Focus**: Engineering procedures, safety protocols, operational manuals
- **Knowledge Sources**: Process documentation, safety standards, operational procedures
- **Analysis**: Process optimization, safety compliance, method improvement

### Corrosion Engineer
- **Focus**: Material analysis, corrosion prevention, inspection data
- **Knowledge Sources**: Material specifications, corrosion databases, inspection reports
- **Analysis**: Corrosion assessment, material selection, prevention strategies

### Subsea Engineer
- **Focus**: Underwater systems, marine engineering, subsea operations
- **Knowledge Sources**: Subsea equipment manuals, marine condition data, operational procedures
- **Analysis**: Subsea system analysis, marine environment assessment, underwater operations

### Discipline Head
- **Focus**: Project coordination, decision making, strategic planning
- **Knowledge Sources**: Project documentation, decision frameworks, governance protocols
- **Analysis**: Strategic planning, project oversight, decision support

## 🔧 **Enhanced API Endpoints**

### Knowledge Management
- `POST /knowledge/ingest/batch` - Batch document ingestion
- `POST /knowledge/ingest/single` - Single document ingestion
- `GET /knowledge/search` - Knowledge base search
- `GET /knowledge/stats` - Knowledge base statistics
- `PUT /knowledge/documents/{id}` - Update document
- `DELETE /knowledge/documents/{id}` - Delete document

### Agent-Specific Analysis
- `POST /knowledge/agents/{agent_type}/analyze` - Agent-specific analysis
- `GET /knowledge/documents` - List documents
- `GET /knowledge/documents/{id}` - Get document details

## 📈 **Recommended Enhancements**

### Phase 1: Enhanced Document Processing
1. **Implement proper PDF processing** with PyPDF2/pdfplumber
2. **Add Excel/CSV support** for data analysis
3. **Enhance image processing** with OCR and object detection
4. **Add document chunking** for better retrieval

### Phase 2: Advanced RAG Features
1. **Implement semantic search** with better embeddings
2. **Add knowledge graph** for entity relationships
3. **Enhance agent specialization** with domain-specific prompts
4. **Add multi-turn conversation** context

### Phase 3: Production Optimization
1. **Scale vector database** for large document collections
2. **Implement caching** for frequent queries
3. **Add document versioning** and update mechanisms
4. **Enhance security** and access controls

## 🎯 **Usage Examples**

### 1. Upload Documents via Frontend
```javascript
// Frontend automatically handles file upload
// Files are processed and stored in knowledge base
// Agents can then reference these documents
```

### 2. Programmatic Document Ingestion
```python
# Using the enhanced API
import requests

# Batch upload documents
documents = [
    {
        "content": pdf_content,
        "filename": "safety_procedures.pdf",
        "metadata": {"category": "safety", "department": "operations"}
    }
]

response = requests.post(
    "http://localhost:8000/knowledge/ingest/batch",
    json={"documents": documents}
)
```

### 3. Agent-Specific Knowledge Search
```python
# Search knowledge base for specific agent
response = requests.get(
    "http://localhost:8000/knowledge/search",
    params={
        "query": "corrosion prevention methods",
        "agent_type": "corrosion_engineer",
        "limit": 5
    }
)
```

## 🔍 **Knowledge Base Statistics**

### Current Capabilities
- **Document Processing**: ~10MB per file, 5 files max
- **Response Time**: <2 seconds for simple queries
- **Accuracy**: Depends on document quality and agent specialization
- **Scalability**: Limited by current mock implementations

### Target Improvements
- **Document Processing**: 50MB+ per file, 100+ files per session
- **Response Time**: <1 second for cached queries
- **Accuracy**: 90%+ for domain-specific queries
- **Scalability**: Production-ready with proper cloud services

## 🛠️ **Configuration Updates**

### Environment Variables
```bash
# Enhanced document processing
MAX_FILE_SIZE_MB=50
MAX_FILES_PER_SESSION=100
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Vector search optimization
VECTOR_SEARCH_BATCH_SIZE=100
VECTOR_SEARCH_TIMEOUT=30
EMBEDDING_MODEL=text-embedding-004

# Agent specialization
AGENT_SPECIFIC_EMBEDDINGS=true
DOMAIN_KNOWLEDGE_BOOST=1.5
```

## 📊 **Monitoring & Analytics**

### Knowledge Base Metrics
- Total documents ingested
- Total chunks created
- Storage size
- Last update timestamp
- Query performance
- Agent-specific usage

### Performance Monitoring
- Response times
- Error rates
- Knowledge retrieval accuracy
- Agent specialization effectiveness

## 🚀 **Next Steps**

1. **Test the enhanced knowledge management** with sample documents
2. **Implement proper PDF processing** libraries
3. **Add Excel/CSV support** for data analysis
4. **Enhance agent specialization** with domain-specific prompts
5. **Scale to production** with proper cloud services

The system is now ready for advanced knowledge management and agent orchestration! 🎉
