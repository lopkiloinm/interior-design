import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads directory in /tmp for serverless
UPLOAD_DIR = "/tmp/uploads"

@app.get("/api/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve uploaded files"""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content type
        content_type = "image/jpeg"
        if filename.endswith(".png"):
            content_type = "image/png"
        elif filename.endswith(".gif"):
            content_type = "image/gif"
        elif filename.endswith(".webp"):
            content_type = "image/webp"
        
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=filename
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Handler for Vercel
handler = app 