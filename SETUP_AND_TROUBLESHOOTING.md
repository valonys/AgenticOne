# AgenticOne Setup and Troubleshooting Guide

## 🚀 Quick Setup

### Prerequisites
- Node.js 18+
- Python 3.8+
- Google Cloud Project with OAuth 2.0 credentials

### Frontend Setup
```bash
# Install dependencies
npm install

# Copy environment template
cp env.example .env.local

# Edit .env.local with your actual values
# Start development server
npm run dev
```

### Backend Setup
```bash
cd agenticone-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your actual values
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Environment Configuration

### Frontend (.env.local)
```env
VITE_GOOGLE_CLIENT_ID=your-google-client-id-here
VITE_GOOGLE_CLIENT_SECRET=your-google-client-secret-here
VITE_API_URL=http://localhost:8000
VITE_FRONTEND_URL=http://localhost:3000
VITE_GEMINI_API_KEY=your-gemini-api-key-here
VITE_JWT_SECRET=your-jwt-secret-here
```

### Backend (.env)
```env
GOOGLE_CLOUD_PROJECT=your-project-id-here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro
VECTOR_SEARCH_INDEX_ID=your-vector-search-index-id
FIRESTORE_PROJECT_ID=your-project-id-here
CLOUD_STORAGE_BUCKET=your-storage-bucket-name
SECRET_KEY=your-super-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🔐 Google OAuth Setup

### 1. Google Cloud Console
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API and Google OAuth2 API

### 2. OAuth 2.0 Credentials
1. Go to "Credentials" in the API & Services section
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Set application type to "Web application"
4. Add authorized origins: `http://localhost:3000`
5. Add redirect URIs: `http://localhost:3000`

### 3. Environment Variables
Ensure the `.env` file contains:
```env
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_CLOUD_PROJECT=your-project-id-here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://agenticone.vercel.app
```

### 4. Start Backend Server
```bash
cd agenticone/agenticone-backend
source venv/bin/activate
export GOOGLE_CLIENT_SECRET=your-google-client-secret-here
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Important:** The `export GOOGLE_CLIENT_SECRET` command is crucial for the OAuth to work properly.

## 🐛 Common Issues

### OAuth Authentication Issues

#### Issue: "Invalid client" error
**Solution:**
1. Verify client ID in frontend `.env.local`
2. Check that OAuth credentials are correctly configured in Google Cloud Console
3. Ensure authorized origins include your frontend URL

#### Issue: "Redirect URI mismatch" error
**Solution:**
1. Add `http://localhost:3000` to authorized redirect URIs in Google Cloud Console
2. Check that `VITE_FRONTEND_URL` matches your actual frontend URL

#### Issue: CORS errors
**Solution:**
1. Verify `ALLOWED_ORIGINS` in backend `.env` includes your frontend URL
2. Check that backend is running on the correct port (8000)
3. Ensure frontend is making requests to the correct backend URL

### Backend Connection Issues

#### Issue: "Connection refused" error
**Solution:**
1. Verify backend is running on port 8000
2. Check `VITE_API_URL` in frontend `.env.local`
3. Ensure no firewall is blocking the connection

#### Issue: "Invalid API key" error
**Solution:**
1. Verify `VITE_GEMINI_API_KEY` is correctly set
2. Check that the API key has proper permissions
3. Ensure the key is not expired

### Environment Variable Issues

#### Issue: Environment variables not loading
**Solution:**
1. Ensure `.env.local` file exists in the frontend root directory
2. Check that variable names start with `VITE_` for frontend
3. Restart the development server after changing environment variables

#### Issue: Backend environment variables not found
**Solution:**
1. Ensure `.env` file exists in `agenticone-backend` directory
2. Check that all required variables are set
3. Verify file permissions allow reading the `.env` file

## 🔍 Debugging Steps

### 1. Check Environment Variables
```bash
# Frontend
cat .env.local

# Backend
cat agenticone-backend/.env
```

### 2. Verify OAuth Configuration
1. Check that client ID matches in both Google Cloud Console and frontend
2. Verify redirect URIs are correctly configured
3. Ensure the OAuth consent screen is properly set up

### 3. Test API Endpoints
```bash
# Test backend health
curl http://localhost:8000/health

# Test OAuth endpoint
curl -X POST http://localhost:8000/api/oauth/token \
  -H "Content-Type: application/json" \
  -d '{"code":"test","redirect_uri":"http://localhost:3000","client_id":"your-google-client-id-here","code_verifier":"test"}'
```

### 4. Check Logs
```bash
# Backend logs
cd agenticone-backend
uvicorn app.main:app --reload --log-level debug

# Frontend logs (in browser console)
# Check for CORS errors, authentication errors, etc.
```

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Vite Documentation](https://vitejs.dev/)

## 🆘 Getting Help

If you're still experiencing issues:

1. Check the browser console for error messages
2. Review the backend logs for detailed error information
3. Verify all environment variables are correctly set
4. Ensure all dependencies are properly installed
5. Check that all required services (Google Cloud, OAuth) are properly configured

For additional support, please refer to the main README.md file or create an issue in the repository.
