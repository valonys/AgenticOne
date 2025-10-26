# AgenticOne - AI-Powered Document Analysis Platform

A comprehensive AI platform for analyzing inspection reports and generating professional insights using specialized AI agents.

## 🚀 Features

- **Multi-Specialist AI Agents**: Corrosion Engineer, Subsea Engineer, Methods Specialist, Discipline Head
- **Document Upload & Analysis**: PDF, Word, Images with AI-powered insights
- **Multi-Format Reports**: HTML, PDF, Markdown with professional styling
- **Google OAuth Integration**: Secure authentication
- **Real-time Chat Interface**: Interactive consultation with AI specialists
- **Vertex AI Integration**: Advanced AI analysis capabilities

## 🏗️ Architecture

### Frontend (React + Vite)
- Modern React application with TypeScript
- Google OAuth 2.0 authentication
- Real-time chat interface
- Document upload capabilities
- Multi-format report generation

### Backend (FastAPI + Python)
- RESTful API with FastAPI
- Google Cloud Platform integration
- Vertex AI for document analysis
- Firestore for data storage
- Cloud Storage for file management
- Vector search for knowledge retrieval

## 🛠️ Local Development Setup

### Prerequisites
- Node.js 18+
- Python 3.9+
- Google Cloud Platform account
- Google OAuth credentials

### Frontend Setup
```bash
# Install dependencies
npm install

# Copy environment template
cp env.template .env.local

# Edit .env.local with your credentials
# Start development server
npm run dev
```

### Backend Setup
```bash
# Navigate to backend directory
cd agenticone-backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.template .env

# Edit .env with your credentials
# Start development server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Production Deployment

### Vercel Deployment

#### Frontend Deployment
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

#### Backend Deployment
1. Create a separate Vercel project for backend
2. Configure Python runtime
3. Set environment variables
4. Deploy with automatic scaling

### Environment Variables

#### Frontend (Vercel)
```
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_GOOGLE_CLIENT_SECRET=your_google_client_secret
VITE_API_URL=https://your-backend-url.vercel.app
VITE_FRONTEND_URL=https://your-frontend-url.vercel.app
VITE_GEMINI_API_KEY=your_gemini_api_key
VITE_DEBUG=false
VITE_ENABLE_GUEST_MODE=true
VITE_JWT_SECRET=your_jwt_secret
VITE_TOKEN_EXPIRE_MINUTES=30
```

#### Backend (Vercel)
```
GOOGLE_CLOUD_PROJECT=your_project_id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-pro
VECTOR_SEARCH_INDEX_ID=your_index_id
FIRESTORE_PROJECT_ID=your_project_id
CLOUD_STORAGE_BUCKET=your_bucket_name
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

## 📚 API Documentation

### Core Endpoints
- `GET /health` - Health check
- `GET /agents` - List available AI agents
- `POST /api/auth/token` - OAuth token exchange
- `POST /api/document-analysis/upload-and-analyze` - Document upload and analysis
- `POST /api/chat/enhanced-chat` - Chat with AI agents
- `GET /api/reports/download/{format}/{report_id}` - Download generated reports

### Document Analysis
- Upload inspection reports and images
- AI-powered analysis by specialist agents
- Multi-format report generation
- Professional insights and recommendations

## 🔧 Configuration

### Google Cloud Setup
1. Create a Google Cloud Project
2. Enable Vertex AI, Firestore, and Cloud Storage APIs
3. Create a service account with appropriate permissions
4. Set up OAuth 2.0 credentials
5. Configure Vector Search index

### OAuth Configuration
1. Create OAuth 2.0 credentials in Google Cloud Console
2. Add authorized redirect URIs:
   - `http://localhost:3000` (development)
   - `https://your-frontend-url.vercel.app` (production)
3. Set client ID and secret in environment variables

## 🧪 Testing

### Local Testing
```bash
# Frontend
npm run dev
# Visit http://localhost:3000

# Backend
python3 -m uvicorn app.main:app --reload
# API available at http://localhost:8000
```

### Production Testing
1. Deploy to Vercel
2. Test authentication flow
3. Test document upload
4. Test report generation
5. Verify all endpoints are working

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

This is a private project. For access and contribution guidelines, contact the development team.

## 📞 Support

For technical support and questions, contact the development team or create an issue in the repository.