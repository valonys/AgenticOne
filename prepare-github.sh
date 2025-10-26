#!/bin/bash

# AgenticOne GitHub Preparation Script
echo "🚀 Preparing AgenticOne for GitHub deployment..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the AgenticOne-main directory"
    exit 1
fi

# Create backup of current state
echo "📦 Creating backup of current state..."
cp -r /Users/atalibamiguel/Documents/AgenticOne-Project/AgenticOne-main /Users/atalibamiguel/Documents/AgenticOne-Project/AgenticOne-backup-$(date +%Y%m%d_%H%M%S)

# Remove sensitive files and directories
echo "🔒 Removing sensitive files and directories..."

# Remove environment files
rm -f .env .env.local .env.production production.env
rm -f agenticone-backend/.env

# Remove service account files
rm -f agenticone-service-account.json
rm -f agenticone-ed918-9678627db0c2.json
rm -f agenticone-backend/agenticone-service-account.json
rm -f agenticone-backend/agenticone-ed918-9678627db0c2.json

# Remove generated reports and conversations
rm -rf agenticone-backend/reports/
rm -rf agenticone-backend/conversations/
rm -rf agenticone-backend/venv/
rm -rf agenticone-backend/__pycache__/
rm -rf agenticone-backend/*.pyc

# Remove node_modules and build files
rm -rf node_modules/
rm -rf dist/
rm -rf build/

# Remove IDE and OS files
rm -rf .vscode/
rm -rf .idea/
rm -f .DS_Store
rm -f agenticone-backend/.DS_Store

# Remove temporary files
rm -rf agenticone-backend/temp/
rm -rf agenticone-backend/logs/
rm -rf agenticone-backend/uploads/

echo "✅ Sensitive files removed"

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    echo "📝 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: AgenticOne MVP"
else
    echo "📝 Git repository already exists"
fi

# Check git status
echo "📊 Git status:"
git status

echo ""
echo "🎉 Preparation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the changes: git status"
echo "2. Add any additional files: git add ."
echo "3. Commit changes: git commit -m 'Prepare for production deployment'"
echo "4. Create GitHub repository"
echo "5. Add remote: git remote add origin https://github.com/yourusername/agenticone.git"
echo "6. Push to GitHub: git push -u origin main"
echo ""
echo "🔧 After pushing to GitHub:"
echo "1. Connect repository to Vercel"
echo "2. Set environment variables in Vercel dashboard"
echo "3. Deploy frontend and backend separately"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
