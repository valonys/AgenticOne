#!/bin/bash

# AgenticOne Deployment Script
echo "🚀 Starting AgenticOne Deployment to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel:"
    vercel login
fi

echo "📁 Deploying Frontend..."
cd /Users/atalibamiguel/Documents/AgenticOne-Project/AgenticOne-main

# Deploy frontend
echo "🌐 Deploying frontend to Vercel..."
vercel --prod --yes

# Get the frontend URL
FRONTEND_URL=$(vercel ls | grep agenticone | head -1 | awk '{print $2}')
echo "✅ Frontend deployed to: https://$FRONTEND_URL"

echo "📁 Deploying Backend..."
cd /Users/atalibamiguel/Documents/AgenticOne-Project/AgenticOne-main/agenticone-backend

# Deploy backend
echo "🔧 Deploying backend to Vercel..."
vercel --prod --yes

# Get the backend URL
BACKEND_URL=$(vercel ls | grep agenticone-backend | head -1 | awk '{print $2}')
echo "✅ Backend deployed to: https://$BACKEND_URL"

echo ""
echo "🎉 Deployment Complete!"
echo "Frontend: https://$FRONTEND_URL"
echo "Backend: https://$BACKEND_URL"
echo ""
echo "📋 Next Steps:"
echo "1. Update environment variables in Vercel dashboard"
echo "2. Update Google OAuth redirect URIs"
echo "3. Test the deployed application"
echo "4. Share with beta users for feedback"
echo ""
echo "🔧 Environment Variables to Set:"
echo "Frontend:"
echo "  VITE_API_URL=https://$BACKEND_URL"
echo "  VITE_FRONTEND_URL=https://$FRONTEND_URL"
echo ""
echo "Backend:"
echo "  ALLOWED_ORIGINS=https://$FRONTEND_URL"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
