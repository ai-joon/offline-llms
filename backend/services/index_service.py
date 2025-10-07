import os
from pathlib import Path
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

from core.config import settings
import sys
from pathlib import Path as _Path

# Ensure the project root (containing `loader.py`) is on sys.path
_PROJECT_ROOT = _Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from ai.loader import get_or_create_pdf_index, load_index, get_pdf_index_name

class IndexService:
    def __init__(self):
        self.emb_model = settings.ollama_embed_model
        self.base_url = settings.ollama_host
        self.indices_dir = Path(settings.faiss_index_dir)
        self.global_index_dir = Path(settings.faiss_global_index_dir)
    
    async def get_or_create_pdf_index(self, pdf_path: str) -> FAISS:
        """Get or create FAISS index for a specific PDF"""
        try:
            # Use the loader function from the main project
            db = get_or_create_pdf_index(
                pdf_path=pdf_path,
                indices_dir=self.indices_dir,
                emb_model=self.emb_model,
                base_url=self.base_url
            )
            return db
        except Exception as e:
            raise Exception(f"Failed to create/load index for {pdf_path}: {str(e)}")
    
    async def get_global_index(self) -> Optional[FAISS]:
        """Get the global FAISS index if it exists"""
        try:
            if not self.global_index_dir.exists():
                return None
            
            db = load_index(
                index_dir=self.global_index_dir,
                emb_model=self.emb_model,
                base_url=self.base_url
            )
            return db
        except Exception as e:
            print(f"Failed to load global index: {e}")
            return None
    
    def index_exists(self, pdf_path: str) -> bool:
        """Check if an index exists for a specific PDF"""
        try:
            index_name = get_pdf_index_name(pdf_path)
            index_path = self.indices_dir / index_name
            return index_path.exists() and (index_path / "index.faiss").exists()
        except Exception:
            return False
    
    def get_index_info(self, pdf_path: str) -> dict:
        """Get information about an index"""
        try:
            index_name = get_pdf_index_name(pdf_path)
            index_path = self.indices_dir / index_name
            
            if not index_path.exists():
                return {"exists": False}
            
            # Get file sizes
            faiss_file = index_path / "index.faiss"
            pkl_file = index_path / "index.pkl"
            
            info = {
                "exists": True,
                "index_name": index_name,
                "index_path": str(index_path),
                "faiss_size": faiss_file.stat().st_size if faiss_file.exists() else 0,
                "pkl_size": pkl_file.stat().st_size if pkl_file.exists() else 0,
            }
            
            return info
        except Exception as e:
            return {"exists": False, "error": str(e)}
