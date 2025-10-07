from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    api_title: str = "AI Chatbot API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # CORS Settings
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Ollama Settings
    ollama_host: str = "http://localhost:11434"
    ollama_embed_model: str = "nomic-embed-text"
    ollama_llm_model: str = "qwen2.5:3b-instruct"
    
    # FAISS Settings
    faiss_index_dir: str = "faiss_indices"
    faiss_global_index_dir: str = "faiss_index"
    
    # PDF Settings
    pdf_directory: str = "docx"
    max_pdf_size: int = 100 * 1024 * 1024  # 100MB
    
    # Chat Settings
    default_top_k: int = 4
    default_max_tokens: int = 256
    default_max_context_chars: int = 4000
    default_retrieval_mode: str = "similarity"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
