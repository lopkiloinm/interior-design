import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import uvicorn
from dotenv import load_dotenv
import logging

from agent import InteriorDesignAgent
from models import AgentStatus, DesignPlan, ShoppingResult

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Interior Design Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Disable credentials when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance storage
agents: Dict[str, InteriorDesignAgent] = {}

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Interior Design Agent API", "status": "running"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Interior Design Agent API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/upload")
async def upload_room_image(file: UploadFile = File(...)):
    """Upload an empty room image to start the design process"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        content = await file.read()
        
        # Create unique session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Save file temporarily
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{session_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        
        return {
            "success": True,
            "session_id": session_id,
            "file_path": file_path,
            "filename": file.filename
        }
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/start/{session_id}")
async def start_agent(session_id: str, background_tasks: BackgroundTasks):
    """Start the autonomous interior design agent"""
    try:
        # Check if agent already exists for this session
        if session_id in agents:
            return {"error": "Agent already running for this session"}
        
        # Get the uploaded file path
        file_path = None
        for filename in os.listdir("uploads"):
            if filename.startswith(session_id):
                file_path = f"uploads/{filename}"
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail="No uploaded image found for this session")
        
        # Create new agent instance
        agent = InteriorDesignAgent(session_id, file_path)
        agents[session_id] = agent
        
        # Start agent in background
        background_tasks.add_task(agent.run)
        
        return {
            "success": True,
            "message": "Agent started successfully",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Agent start error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/status/{session_id}")
async def get_agent_status(session_id: str):
    """Get the current status and progress of the agent"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        return agent.get_status()
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/plan/{session_id}")
async def get_design_plan(session_id: str):
    """Get the current design plan in markdown format"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        return {
            "plan": agent.get_plan_markdown(),
            "status": agent.status.value
        }
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        logger.error(f"Plan error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/results/{session_id}")
async def get_design_results(session_id: str):
    """Get the final design results including generated room image"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        if agent.status != AgentStatus.COMPLETED:
            return {"error": "Design not yet completed", "status": agent.status.value}
        
        return agent.get_final_results()
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        logger.error(f"Results error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/agent/{session_id}")
async def stop_agent(session_id: str):
    """Stop and clean up an agent session"""
    try:
        if session_id in agents:
            agent = agents[session_id]
            agent.stop()
            del agents[session_id]
            
            # Clean up uploaded files
            for filename in os.listdir("uploads"):
                if filename.startswith(session_id):
                    os.remove(f"uploads/{filename}")
            
            return {"success": True, "message": "Agent stopped and cleaned up"}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")
    except Exception as e:
        logger.error(f"Stop error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        reload_excludes=["**/.venv/**", "**/venv/**", "**/__pycache__/**", "**/*.pyc", "**/uploads/**", ".venv/**", "venv/**"]
    ) 