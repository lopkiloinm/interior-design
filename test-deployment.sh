#!/bin/bash

echo "🧪 Testing Interior Design Agent Deployment..."
echo ""

# Function to test endpoint
test_endpoint() {
    local url=$1
    local name=$2
    
    echo -n "Testing $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" = "200" ]; then
        echo "✅ Success (200 OK)"
        return 0
    else
        echo "❌ Failed (HTTP $response)"
        return 1
    fi
}

# Get API URL from user
echo "Enter your deployed backend URL (e.g., https://your-app.railway.app):"
read -r BACKEND_URL

# Remove trailing slash if present
BACKEND_URL=${BACKEND_URL%/}

echo ""
echo "🔍 Running tests..."
echo ""

# Test endpoints
test_endpoint "$BACKEND_URL/docs" "FastAPI Documentation"
test_endpoint "$BACKEND_URL/api/health" "Health Check"

echo ""
echo "📝 Testing API response..."
health_response=$(curl -s "$BACKEND_URL/api/health" 2>/dev/null)
if [ -n "$health_response" ]; then
    echo "✅ Health check response:"
    echo "$health_response" | python3 -m json.tool 2>/dev/null || echo "$health_response"
fi

echo ""
echo "🎯 Summary:"
echo "- Backend URL: $BACKEND_URL"
echo "- Make sure to set this URL as VITE_API_URL in your frontend deployment"
echo "- Ensure all environment variables are set in your deployment platform" 