from typing import Optional
import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from core.config import settings

# Global database instance
_db: Optional[FAISS] = None
_current_pdf_path: Optional[str] = None

async def initialize_db():
    """Initialize the database connection"""
    global _db, _current_pdf_path
    _db = None
    _current_pdf_path = None
    print("📚 Database initialized")

def get_db() -> Optional[FAISS]:
    """Get the current database instance"""
    return _db

def set_db(db: FAISS, pdf_path: Optional[str] = None):
    """Set the current database instance"""
    global _db, _current_pdf_path
    _db = db
    _current_pdf_path = pdf_path

def get_current_pdf_path() -> Optional[str]:
    """Get the current PDF path"""
    return _current_pdf_path

def clear_db():
    """Clear the current database instance"""
    global _db, _current_pdf_path
    _db = None
    _current_pdf_path = None
