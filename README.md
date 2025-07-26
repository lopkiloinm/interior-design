# Interior Design Agent

An autonomous AI agent that transforms empty rooms into beautifully designed spaces using GPT-4.1-mini and Arcade Google Shopping SDK.

## 🌟 Features

- **Autonomous Design Process**: Upload a photo of an empty room and let the AI handle everything
- **Room Analysis**: Uses GPT-4.1-mini with vision capabilities to analyze room dimensions, lighting, and features
- **Smart Planning**: Creates detailed interior design plans with furniture recommendations
- **Furniture Shopping**: Searches real products using Google Shopping via Arcade API
- **Design Generation**: Creates detailed descriptions of the final room design
- **Real-time Progress**: Track the agent's progress through each step
- **Markdown Reports**: Get detailed design plans in well-structured markdown

## 🚀 Deployment Options

This app uses FastAPI backend which works best on platforms that support full Python applications.

### Option 1: Railway (Recommended - Easiest)

1. **Sign up** at [railway.app](https://railway.app)

2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Deploy**:
   ```bash
   railway login
   railway link
   railway up
   ```

4. **Add environment variables** in Railway dashboard:
   - `OPENAI_API_KEY`
   - `ARCADE_API_KEY`
   - `USER_ID`

5. **Deploy frontend separately** on Vercel:
   ```bash
   cd frontend
   vercel
   ```

### Option 2: Render

1. **Sign up** at [render.com](https://render.com)

2. **Connect your GitHub repo**

3. **Create new Web Service** with:
   - Runtime: Python
   - Build: `pip install -r requirements.txt`
   - Start: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Add environment variables** in Render dashboard

### Option 3: Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create app and deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set ARCADE_API_KEY=your_key
   heroku config:set USER_ID=your_id
   ```

### Option 4: Docker + Any Cloud

1. **Create Dockerfile** (we can add this if needed)
2. Deploy to:
   - Google Cloud Run
   - AWS App Runner
   - Azure Container Apps
   - DigitalOcean App Platform

### Frontend Deployment

The frontend can be deployed separately on:
- **Vercel** (recommended): `cd frontend && vercel`
- **Netlify**: `cd frontend && netlify deploy`
- **GitHub Pages**: With GitHub Actions

### Important Notes

- Update `API_URL` in frontend after backend deployment
- Consider using a database for production (PostgreSQL, MongoDB)
- Use cloud storage for images (S3, Cloudinary)
- Set up proper CORS origins for production

## 🏗️ Architecture

### Backend (FastAPI)
- **Core Logic**: All business logic and AI processing
- **Agent System**: Autonomous agent with state management
- **API Integration**: OpenAI responses API and Arcade Google Shopping
- **Session Management**: Handles multiple concurrent design sessions
- **File Handling**: Room image uploads and storage

### Frontend (React + TypeScript)
- **Pure Presentation**: No business logic, only UI
- **Real-time Updates**: Polls backend for agent status
- **Type Safety**: Full TypeScript implementation
- **Responsive Design**: Works on desktop and mobile

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- Arcade API key and user ID

## 🚀 Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `env.example`:
```bash
cp env.example .env
```

5. Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
ARCADE_API_KEY=your_arcade_api_key_here
ARCADE_USER_ID=your_arcade_user_id_here
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## 🏃‍♂️ Running the Application

### Quick Start (Recommended)

From the project root directory:

**On macOS/Linux:**
```bash
./start.sh
```

**On Windows:**
```batch
start.bat
```

This will start both the backend and frontend servers automatically.

### Manual Start

#### Start the Backend

In the backend directory:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

#### Start the Frontend

In the frontend directory:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 🎯 How to Use

1. Open the application in your browser
2. Upload a photo of an empty room
3. The AI agent will:
   - Analyze the room characteristics
   - Create a design plan
   - Search for suitable furniture
   - Generate the final design
4. Monitor progress in real-time
5. View the complete design plan and results

## 🔄 Agent Workflow

1. **Room Analysis** 🔍
   - Identifies room type and dimensions
   - Analyzes lighting conditions
   - Detects existing features

2. **Design Planning** 📝
   - Selects appropriate design style
   - Creates furniture list
   - Plans room layout

3. **Furniture Shopping** 🛍️
   - Searches Google Shopping for each item
   - Collects product images and prices
   - Builds shopping list

4. **Design Generation** 🎨
   - Creates final room visualization
   - Provides cost estimates
   - Generates design description

## 📚 API Endpoints

- `POST /api/upload` - Upload room image
- `POST /api/agent/start/{session_id}` - Start design agent
- `GET /api/agent/status/{session_id}` - Get agent status
- `GET /api/agent/plan/{session_id}` - Get design plan
- `GET /api/agent/results/{session_id}` - Get final results
- `DELETE /api/agent/{session_id}` - Stop and cleanup session

## 🔧 Configuration

The agent behavior can be customized in `backend/agent.py`:
- Furniture search limits
- Design styles
- Budget constraints
- Room types

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- OpenAI for GPT-4.1-mini
- Arcade for Google Shopping SDK
- React and FastAPI communities 