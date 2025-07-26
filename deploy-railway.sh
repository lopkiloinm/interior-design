#!/bin/bash

echo "🚂 Deploying to Railway..."

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "📝 Logging in to Railway..."
railway login

# Link to project (create new if doesn't exist)
echo "🔗 Linking to Railway project..."
railway link

# Deploy
echo "🚀 Deploying backend..."
railway up

# Get the deployment URL
echo "✅ Backend deployed!"
echo "🔗 Your backend URL is:"
railway status

echo ""
echo "📝 Next steps:"
echo "1. Add environment variables in Railway dashboard:"
echo "   - OPENAI_API_KEY"
echo "   - ARCADE_API_KEY"
echo "   - USER_ID"
echo ""
echo "2. Deploy frontend to Vercel:"
echo "   cd frontend"
echo "   vercel"
echo ""
echo "3. Update VITE_API_URL in Vercel with your Railway backend URL" 