from typing import Optional, Any, Dict
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

from core.config import settings


class ChatService:
    def __init__(self):
        self.llm_model = settings.ollama_llm_model
        self.base_url = settings.ollama_host
    
    async def process_message(
        self,
        message: str,
        db: Optional[Any],
        settings: Dict,
        current_pdf: Optional[str] = None
    ):
        """Process a chat message and return a response"""
        
        # Extract settings
        top_k = settings.get('topK', 4)
        retrieval_mode = settings.get('retrievalMode', 'similarity')
        max_tokens = settings.get('maxTokens', 256)
        max_context_chars = settings.get('maxContextChars', 4000)
        
        ctx_docs = []
        
        if db is None:
            # No index loaded, use general knowledge
            template = (
                "You are a helpful assistant. Answer the question using your general knowledge.\n"
                "Be informative and helpful in your response.\n\n"
                "Question: {question}\nAnswer:"
            )
            prompt = PromptTemplate.from_template(template).format(question=message)
        else:
            # Retrieve context from database
            if retrieval_mode == "mmr":
                retriever = db.as_retriever(
                    search_type="mmr",
                    search_kwargs={"k": top_k, "fetch_k": max(10, top_k * 5)}
                )
            else:
                retriever = db.as_retriever(search_kwargs={"k": top_k})
            
            ctx_docs = retriever.invoke(message)
            
            # Build context from retrieved documents
            parts = []
            total = 0
            for d in ctx_docs:
                text = d.page_content or ""
                remaining = max_context_chars - total
                if remaining <= 0:
                    break
                if len(text) > remaining:
                    text = text[:remaining]
                if text:
                    parts.append(text)
                    total += len(text)
            
            context = "\n\n".join(parts)
            # Sanitize to avoid encoding issues
            context = context.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
            
            # Check if context is empty or very short
            if not context.strip() or len(context.strip()) < 50:
                template = (
                    "You are a helpful assistant. Answer the question using your general knowledge.\n"
                    "Be informative and helpful in your response.\n\n"
                    "Question: {question}\nAnswer:"
                )
                prompt = PromptTemplate.from_template(template).format(question=message)
                ctx_docs = []
            else:
                template = (
                    "You are a helpful assistant. Answer the question using the provided context when available and relevant.\n"
                    "If the context doesn't contain the answer, use your general knowledge to provide a helpful response.\n"
                    "Always be helpful and informative, whether using context or general knowledge.\n\n"
                    "Question: {question}\nContext:\n{context}\nAnswer:"
                )
                prompt = PromptTemplate.from_template(template).format(
                    question=message,
                    context=context
                )
        
        # Generate response using LLM
        llm = OllamaLLM(
            model=self.llm_model,
            base_url=self.base_url,
            temperature=0.2,
            num_predict=max_tokens
        )
        
        answer = llm.invoke(prompt)
        
        # Create response object
        from models.chat import ChatResponse, Source
        sources = [
            Source(content=doc.page_content, metadata=doc.metadata)
            for doc in ctx_docs
        ]
        
        return ChatResponse(answer=answer, sources=sources)
