import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles
import uuid

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload a room image for interior design analysis"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Import and start agent
        from agent import InteriorDesignAgent
        agent = InteriorDesignAgent(file_path)
        
        # Start agent processing in background
        import asyncio
        asyncio.create_task(agent.start())
        
        # Store agent in memory (Note: In production, use Redis or similar)
        if not hasattr(app.state, "agents"):
            app.state.agents = {}
        app.state.agents[agent.session_id] = agent
        
        return JSONResponse({
            "session_id": agent.session_id,
            "status": "processing",
            "message": "Image uploaded successfully. Interior design agent started."
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Handler for Vercel
handler = app 