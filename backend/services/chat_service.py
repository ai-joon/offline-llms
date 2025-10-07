import asyncio
from typing import List, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

from core.config import settings
from models.chat import ChatResponse, Source, ChatSettings

class ChatService:
    def __init__(self):
        self.llm_model = settings.ollama_llm_model
        self.base_url = settings.ollama_host
    
    async def process_message(
        self, 
        message: str, 
        db: Optional[FAISS], 
        settings: ChatSettings,
        current_pdf: Optional[str] = None
    ) -> ChatResponse:
        """Process a chat message and return response"""
        
        if db is None:
            # No database available, use general knowledge
            return await self._generate_general_response(message)
        
        # Retrieve relevant context
        context_docs = await self._retrieve_context(db, message, settings)
        
        # Generate response
        response = await self._generate_response(message, context_docs, settings, current_pdf)
        
        return response
    
    async def _retrieve_context(
        self, 
        db: FAISS, 
        message: str, 
        settings: ChatSettings
    ) -> List[Source]:
        """Retrieve relevant context from the database"""
        try:
            if settings.retrievalMode == "mmr":
                retriever = db.as_retriever(
                    search_type="mmr", 
                    search_kwargs={"k": settings.topK, "fetch_k": max(10, settings.topK * 5)}
                )
            else:
                retriever = db.as_retriever(search_kwargs={"k": settings.topK})
            
            # Retrieve documents
            docs = retriever.invoke(message)
            
            # Convert to Source objects
            sources = []
            total_chars = 0
            
            for doc in docs:
                if total_chars >= settings.maxContextChars:
                    break
                
                content = doc.page_content or ""
                remaining_chars = settings.maxContextChars - total_chars
                
                if len(content) > remaining_chars:
                    content = content[:remaining_chars]
                
                if content.strip():
                    source = Source(
                        content=content,
                        metadata=doc.metadata or {}
                    )
                    sources.append(source)
                    total_chars += len(content)
            
            return sources
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []
    
    async def _generate_response(
        self, 
        message: str, 
        context_docs: List[Source], 
        settings: ChatSettings,
        current_pdf: Optional[str] = None
    ) -> ChatResponse:
        """Generate AI response using context"""
        
        # Prepare context
        context_parts = []
        for doc in context_docs:
            context_parts.append(doc.content)
        context = "\n\n".join(context_parts)
        
        # Check if context is relevant
        if not context.strip() or len(context.strip()) < 50:
            # Use general knowledge template
            template = (
                "You are a helpful assistant. Answer the question using your general knowledge.\n"
                "Be informative and helpful in your response.\n\n"
                "Question: {question}\nAnswer:"
            )
            prompt = PromptTemplate.from_template(template).format(question=message)
            context_docs = []  # No context to show
        else:
            # Use context-aware template
            template = (
                "You are a helpful assistant. Answer the question using the provided context when available and relevant.\n"
                "If the context doesn't contain the answer, use your general knowledge to provide a helpful response.\n"
                "Always be helpful and informative, whether using context or general knowledge.\n\n"
                "Question: {question}\nContext:\n{context}\nAnswer:"
            )
            prompt = PromptTemplate.from_template(template).format(question=message, context=context)
        
        # Generate response using Ollama
        try:
            llm = OllamaLLM(
                model=self.llm_model, 
                base_url=self.base_url, 
                temperature=0.2, 
                num_predict=settings.maxTokens
            )
            
            # Generate response
            response_text = await asyncio.to_thread(llm.invoke, prompt)
            
            return ChatResponse(
                answer=response_text,
                sources=context_docs if settings.showContext else []
            )
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return ChatResponse(
                answer="I apologize, but I encountered an error while processing your request. Please try again.",
                sources=[]
            )
    
    async def _generate_general_response(self, message: str) -> ChatResponse:
        """Generate response using general knowledge only"""
        try:
            template = (
                "You are a helpful assistant. Answer the question using your general knowledge.\n"
                "Be informative and helpful in your response.\n\n"
                "Question: {question}\nAnswer:"
            )
            prompt = PromptTemplate.from_template(template).format(question=message)
            
            llm = OllamaLLM(
                model=self.llm_model, 
                base_url=self.base_url, 
                temperature=0.2, 
                num_predict=settings.default_max_tokens
            )
            
            response_text = await asyncio.to_thread(llm.invoke, prompt)
            
            return ChatResponse(
                answer=response_text,
                sources=[]
            )
            
        except Exception as e:
            print(f"Error generating general response: {e}")
            return ChatResponse(
                answer="I apologize, but I'm currently unable to process your request. Please try again later.",
                sources=[]
            )
