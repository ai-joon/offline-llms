from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PDFDocument(BaseModel):
    name: str
    path: str
    size: Optional[int] = None
    lastModified: Optional[datetime] = None

class LoadPDFRequest(BaseModel):
    pdf_path: str

class PDFInfo(BaseModel):
    name: str
    path: str
    size: int
    lastModified: datetime
    pageCount: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
