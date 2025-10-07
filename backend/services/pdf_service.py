import os
import glob
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import PyPDF2

from core.config import settings
from models.pdf import PDFDocument, PDFInfo

class PDFService:
    def __init__(self):
        self.pdf_directory = Path(settings.pdf_directory)
    
    async def get_available_pdfs(self) -> List[PDFDocument]:
        """Get list of available PDF documents"""
        pdfs = []
        
        if not self.pdf_directory.exists():
            return pdfs
        
        # Find all PDF files
        pdf_files = glob.glob(str(self.pdf_directory / "*.pdf"))
        
        for pdf_path in pdf_files:
            try:
                pdf_path = Path(pdf_path)
                stat = pdf_path.stat()
                
                pdf_doc = PDFDocument(
                    name=pdf_path.name,
                    path=str(pdf_path),
                    size=stat.st_size,
                    lastModified=datetime.fromtimestamp(stat.st_mtime)
                )
                pdfs.append(pdf_doc)
            except Exception as e:
                print(f"Error processing PDF {pdf_path}: {e}")
                continue
        
        # Sort by name
        pdfs.sort(key=lambda x: x.name)
        return pdfs
    
    async def get_pdf_info(self, pdf_name: str) -> PDFInfo:
        """Get detailed information about a specific PDF"""
        pdf_path = self.pdf_directory / pdf_name
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_name}")
        
        stat = pdf_path.stat()
        
        # Try to get PDF metadata
        page_count = None
        title = None
        author = None
        subject = None
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    title = pdf_reader.metadata.get('/Title')
                    author = pdf_reader.metadata.get('/Author')
                    subject = pdf_reader.metadata.get('/Subject')
        except Exception as e:
            print(f"Error reading PDF metadata: {e}")
        
        return PDFInfo(
            name=pdf_path.name,
            path=str(pdf_path),
            size=stat.st_size,
            lastModified=datetime.fromtimestamp(stat.st_mtime),
            pageCount=page_count,
            title=title,
            author=author,
            subject=subject
        )
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """Validate if a PDF file is valid and accessible"""
        try:
            if not os.path.exists(pdf_path):
                return False
            
            # Check file size
            if os.path.getsize(pdf_path) > settings.max_pdf_size:
                return False
            
            # Try to open with PyPDF2
            with open(pdf_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            
            return True
        except Exception:
            return False
