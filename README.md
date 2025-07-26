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

## 🚀 Deployment to Vercel

### Prerequisites
1. A Vercel account
2. Vercel CLI installed (`npm i -g vercel`)
3. Environment variables ready:
   - `OPENAI_API_KEY`
   - `ARCADE_API_KEY`
   - `USER_ID` (for Arcade)

### Deployment Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy the project**:
   ```bash
   vercel
   ```

4. **Set environment variables** in Vercel dashboard:
   - Go to your project settings
   - Navigate to "Environment Variables"
   - Add the following:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `ARCADE_API_KEY`: Your Arcade API key
     - `USER_ID`: Your Arcade user ID

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Project Structure for Vercel

- `/api` - Serverless Python functions
- `/frontend` - React/Vite frontend
- `vercel.json` - Deployment configuration
- `requirements.txt` - Python dependencies

### Notes
- The backend runs as serverless functions
- Uploads are stored temporarily in `/tmp`
- For production use, consider using external storage (S3, Cloudinary, etc.)

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