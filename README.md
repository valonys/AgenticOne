# 🤖 AgenticOne - AI-Powered Engineering Analysis Platform

<div align="center">
  <img src="https://github.com/valonys/DigiTwin/blob/29dd50da95bec35a5abdca4bdda1967f0e5efff6/ValonyLabs_Logo.png?raw=true" width="100" alt="ValonLabs Logo" />
  <h3>AI Beyond Compare</h3>
</div>

## 🎯 **Overview**

AgenticOne is an intelligent engineering analysis platform featuring specialized AI agents that provide expert domain-specific insights and recommendations for engineering teams.

## 🤖 **AI Specialists**

- **Methods Specialist** - Optimizes operational procedures and engineering methods
- **Corrosion Engineer** - Analyzes corrosion issues and prevention strategies  
- **Subsea Engineer** - Handles underwater operations and marine engineering
- **Discipline Head** - Coordinates project activities and strategic decisions

## ✨ **Key Features**

- 🗣️ **Conversational AI** - Natural language interaction with specialized agents
- 📄 **Document Processing** - Upload and analyze engineering documents
- 🔍 **RAG-Powered Search** - Intelligent knowledge retrieval from multiple sources
- 🔐 **OAuth 2.0 Authentication** - Secure Google sign-in with PKCE
- 👤 **Guest Mode** - Access without authentication
- 📊 **Token Management** - Usage tracking and limits
- 🎨 **Modern UI** - Responsive dark theme interface

## 🚀 **Quick Start**

### Prerequisites
- Node.js 18+
- Python 3.8+
- Google Cloud credentials (for OAuth)

### Frontend Setup
```bash
# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API keys

# Start development server
npm run dev
```

### Backend Setup
```bash
cd agenticone-backend

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your configuration

# Start FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 **Configuration**

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add authorized origins: `http://localhost:3000`
4. Add redirect URIs: `http://localhost:3000`

### Environment Variables
- `GEMINI_API_KEY` - Google Gemini API key
- `GOOGLE_CLIENT_ID` - OAuth client ID
- `GOOGLE_CLIENT_SECRET` - OAuth client secret

## 📁 **Project Structure**

```
agenticone/
├── frontend/                 # React + TypeScript
│   ├── components/          # UI components
│   ├── auth-oauth2.ts      # OAuth 2.0 implementation
│   └── index.tsx           # Main application
├── agenticone-backend/      # FastAPI + Python
│   ├── app/
│   │   ├── agents/         # AI specialist agents
│   │   ├── services/       # RAG, vision, reports
│   │   └── api/           # OAuth handlers
│   └── requirements.txt
└── docs/                   # Documentation
```

## 🛠️ **Technologies**

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI, Python, Vertex AI Gemini
- **Authentication**: OAuth 2.0 with PKCE
- **Database**: Firestore, Vector Search
- **Deployment**: Google Cloud Run, Docker

## 📚 **Documentation**

- [OAuth 2.0 Implementation Guide](OAUTH2_IMPLEMENTATION.md)
- [Google Cloud Console Setup](GOOGLE_CLOUD_CONSOLE_FIX.md)
- [Backend API Documentation](agenticone-backend/README.md)
- [Deployment Guide](agenticone-backend/DEPLOYMENT.md)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

<div align="center">
  <p>Built with ❤️ by <a href="https://valonylabs.com">ValonyLabs</a></p>
</div>
