from fastapi import APIRouter, HTTPException
from typing import List
import asyncio

from core.config import settings
from core.database import get_db, get_current_pdf_path
from services.chat_service import ChatService
from models.chat import ChatRequest, ChatResponse, Source

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the AI chatbot"""
    try:
        # Get current database
        db = get_db()
        current_pdf = get_current_pdf_path()
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Process the message
        response = await chat_service.process_message(
            message=request.message,
            db=db,
            settings=request.settings,
            current_pdf=current_pdf
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/chat/history")
async def get_chat_history():
    """Get chat history (placeholder for future implementation)"""
    return {"message": "Chat history feature coming soon"}

@router.delete("/chat/history")
async def clear_chat_history():
    """Clear chat history (placeholder for future implementation)"""
    return {"message": "Chat history cleared"}
