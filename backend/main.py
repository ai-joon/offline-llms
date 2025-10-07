from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import glob
from pathlib import Path
from typing import List, Optional
import uvicorn

from api.routes import chat, pdfs, health
from core.config import settings
from core.database import get_db, initialize_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_db()
    print("AI Chatbot API started successfully!")
    yield
    # Shutdown
    print("AI Chatbot API shutting down...")

app = FastAPI(
    title="AI Chatbot API",
    description="Backend API for AI Chatbot with Document RAG",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default dev port
        "http://127.0.0.1:5173"
    ],
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

if __name__ == "__main__":
    port = int(os.getenv("PORT", "16005"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
