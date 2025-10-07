from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import glob
from pathlib import Path
from typing import List, Optional
import uvicorn

from api.routes import chat, pdfs, health
from core.config import settings
from core.database import get_db, initialize_db

app = FastAPI(
    title="AI Chatbot API",
    description="Backend API for AI Chatbot with Document RAG",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(pdfs.router, prefix="/api", tags=["pdfs"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Mount static files for PDF serving
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    await initialize_db()
    print("🚀 AI Chatbot API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 AI Chatbot API shutting down...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
