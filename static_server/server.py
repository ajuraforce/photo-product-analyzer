"""
Static file server for serving uploaded images
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging

from bot.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Product Cataloger Static Server")

# Ensure uploads directory exists
uploads_dir = Path("static_server/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="static_server/uploads"), name="uploads")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Product Cataloger Static Server", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "uploads_dir": str(uploads_dir.absolute())}

@app.get("/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """Serve uploaded files"""
    file_path = uploads_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

if __name__ == "__main__":
    port = Config.STATIC_SERVER_PORT
    logger.info(f"Starting static server on port {port}")
    uvicorn.run(
        "static_server.server:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )