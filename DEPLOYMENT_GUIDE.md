# AgenticOne Deployment Guide

## 🚀 Vercel Deployment Setup

### Frontend Deployment (Vercel)

#### 1. Prepare Frontend for Deployment

The frontend is already configured for Vercel deployment with:
- ✅ `vercel.json` configuration file
- ✅ Vite build setup
- ✅ Environment variable configuration

#### 2. Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd /Users/atalibamiguel/Documents/AgenticOne-Project/AgenticOne-main

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### 3. Environment Variables in Vercel Dashboard

Set these environment variables in your Vercel project dashboard:

```
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_GOOGLE_CLIENT_SECRET=your_google_client_secret_here
VITE_API_URL=https://agenticone-backend.vercel.app
VITE_FRONTEND_URL=https://agenticone.vercel.app
VITE_GEMINI_API_KEY=your_gemini_api_key_here
VITE_DEBUG=false
VITE_ENABLE_GUEST_MODE=true
VITE_JWT_SECRET=agenticone-secure-key-2024
VITE_TOKEN_EXPIRE_MINUTES=30
```

### Backend Deployment Options

#### Option 1: Vercel (Recommended for MVP)

Create a separate Vercel project for the backend:

```bash
# Create backend directory structure
mkdir agenticone-backend-deploy
cd agenticone-backend-deploy

# Copy backend files
cp -r /Users/atalibamiguel/Documents/AgenticOne-Project/AgenticOne-main/agenticone-backend/* .

# Create requirements.txt for Vercel
echo "fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
google-cloud-aiplatform==1.38.0
google-cloud-firestore==2.13.0
google-cloud-storage==2.10.0
google-auth==2.23.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
requests==2.31.0
numpy==1.24.3
markdown2==2.5.4
reportlab==4.0.4
jinja2==3.1.2
python-multipart==0.0.6" > requirements.txt

# Create vercel.json for backend
cat > vercel.json << 'EOF'
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
EOF

# Deploy backend
vercel --prod
```

#### Option 2: Railway (Alternative)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

#### Option 3: Render (Alternative)

1. Connect GitHub repository to Render
2. Select "Web Service"
3. Configure build and start commands
4. Set environment variables

### Environment Variables for Backend

Set these in your backend deployment platform:

```
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=agenticone-ed918
GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-pro

# Vector Search Configuration
VECTOR_SEARCH_INDEX_ID=3314070982628474880
VECTOR_SEARCH_DIMENSIONS=768

# Firestore Configuration
FIRESTORE_PROJECT_ID=agenticone-ed918
FIRESTORE_DATABASE_ID=(default)

# Cloud Storage Configuration
CLOUD_STORAGE_BUCKET=agenticone_storage_bucket

# Agent Configuration
MAX_ANALYSIS_RETRIES=3
ANALYSIS_TIMEOUT=300

# Report Generation
REPORT_TEMPLATE_PATH=templates/
REPORT_OUTPUT_PATH=reports/

# Security
SECRET_KEY=agenticone-secure-key-2024
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=https://agenticone.vercel.app,https://agenticone-frontend.vercel.app

# Debug Configuration
DEBUG=false
LOG_LEVEL=INFO

# OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Service Account Setup

For production deployment, you'll need to:

1. **Create a proper service account** in Google Cloud Console
2. **Download the JSON key file**
3. **Convert to base64** for environment variable storage:

```bash
# Convert service account to base64
base64 -i service-account.json | tr -d '\n'
```

4. **Set as environment variable** `GOOGLE_APPLICATION_CREDENTIALS_BASE64`
5. **Update backend code** to decode and write the file at runtime

### Testing Production Deployment

1. **Frontend**: Visit `https://agenticone.vercel.app`
2. **Backend**: Test API at `https://agenticone-backend.vercel.app/health`
3. **Authentication**: Test Google OAuth flow
4. **Document Upload**: Test file upload and analysis
5. **Report Generation**: Test report generation workflow

### Monitoring and Debugging

1. **Vercel Analytics**: Enable in Vercel dashboard
2. **Function Logs**: Check Vercel function logs
3. **Error Tracking**: Set up error monitoring
4. **Performance**: Monitor response times

### Next Steps After Deployment

1. **User Testing**: Share with beta users
2. **Feedback Collection**: Set up feedback forms
3. **Performance Optimization**: Based on usage patterns
4. **Feature Iteration**: Based on user feedback
5. **Scaling**: Prepare for increased usage

## 🎯 Production Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed (Vercel/Railway/Render)
- [ ] Environment variables configured
- [ ] Service account credentials set up
- [ ] CORS configured for production domains
- [ ] Google OAuth redirect URIs updated
- [ ] SSL certificates working
- [ ] API endpoints responding
- [ ] Authentication flow working
- [ ] Document upload working
- [ ] Report generation working
- [ ] Error monitoring set up
- [ ] Analytics enabled
- [ ] User feedback collection ready
