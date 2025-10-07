from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List
import os
import glob
from pathlib import Path
from datetime import datetime

from core.config import settings
from core.database import get_db, set_db, get_current_pdf_path
from services.pdf_service import PDFService
from services.index_service import IndexService
from models.pdf import PDFDocument, LoadPDFRequest

router = APIRouter()

@router.get("/pdfs", response_model=List[PDFDocument])
async def get_available_pdfs():
    """Get list of available PDF documents"""
    try:
        pdf_service = PDFService()
        pdfs = await pdf_service.get_available_pdfs()
        return pdfs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load PDFs: {str(e)}")

@router.post("/load-pdf")
async def load_pdf(request: LoadPDFRequest, background_tasks: BackgroundTasks):
    """Load or create index for a specific PDF"""
    try:
        pdf_path = request.pdf_path
        
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Check if it's already loaded
        current_pdf = get_current_pdf_path()
        if current_pdf == pdf_path:
            return {"success": True, "message": "PDF already loaded", "pdf_path": pdf_path}
        
        # Load or create index
        index_service = IndexService()
        db = await index_service.get_or_create_pdf_index(pdf_path)
        
        # Set as current database
        set_db(db, pdf_path)
        
        return {
            "success": True, 
            "message": f"Successfully loaded {os.path.basename(pdf_path)}",
            "pdf_path": pdf_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load PDF: {str(e)}")

@router.get("/pdf-content")
async def get_pdf_content(path: str):
    """Get PDF file content for viewing"""
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        # Security check - ensure path is within allowed directory
        pdf_dir = Path(settings.pdf_directory).resolve()
        pdf_path = Path(path).resolve()
        
        if not str(pdf_path).startswith(str(pdf_dir)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FileResponse(
            path=path,
            media_type="application/pdf",
            filename=os.path.basename(path)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load PDF content: {str(e)}")

@router.get("/pdf-info/{pdf_name}")
async def get_pdf_info(pdf_name: str):
    """Get detailed information about a specific PDF"""
    try:
        pdf_service = PDFService()
        pdf_info = await pdf_service.get_pdf_info(pdf_name)
        return pdf_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PDF info: {str(e)}")
