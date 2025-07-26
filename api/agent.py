import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared agent storage (Note: In production, use Redis or similar)
agents = {}

@app.get("/api/agent/status/{session_id}")
async def get_agent_status(session_id: str):
    """Get the current status and progress of the agent"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        return agent.get_status()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/plan/{session_id}")
async def get_design_plan(session_id: str):
    """Get the design plan in markdown format"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        return {
            "plan": agent.get_plan_markdown(),
            "status": agent.status.value
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Plan error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/results/{session_id}")
async def get_final_results(session_id: str):
    """Get the final design results"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        
        # Check if agent has completed
        if agent.status.value != "completed":
            raise HTTPException(status_code=400, detail="Design not yet completed")
        
        return agent.get_final_results()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Results error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/stop/{session_id}")
async def stop_agent(session_id: str):
    """Stop the agent processing"""
    try:
        if session_id not in agents:
            raise HTTPException(status_code=404, detail="Agent not found for this session")
        
        agent = agents[session_id]
        agent.stop()
        
        return {"status": "stopped", "message": "Agent processing stopped"}
    except Exception as e:
        logger.error(f"Stop error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Handler for Vercel
handler = app 