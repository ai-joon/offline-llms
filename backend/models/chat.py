from pydantic import BaseModel
from typing import List, Optional

class Source(BaseModel):
    content: str
    metadata: dict

class ChatSettings(BaseModel):
    topK: int = 4
    retrievalMode: str = "similarity"
    maxTokens: int = 256
    maxContextChars: int = 4000
    showContext: bool = False

class ChatRequest(BaseModel):
    message: str
    settings: ChatSettings

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
