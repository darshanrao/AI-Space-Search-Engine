"""
RAG Service - Interface to your RAG pipeline.
This is where you'll connect your actual RAG implementation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from models import RAGResponse, Citation, ImageCitation
from settings import settings


class RAGService:
    """Service class for RAG operations."""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=settings.MAX_RESPONSE_TOKENS
        )
    
    def generate_answer(self, question: str, context: Dict[str, Any], conversation_history: List[Tuple[str, str]] = None) -> RAGResponse:
        """
        Generate RAG-powered answer.
        
        This is where you'll integrate with your actual RAG pipeline.
        For now, it returns a mock response in your exact format.
        
        Args:
            question: User's question
            context: Additional context (organism, focus area, etc.)
            conversation_history: Previous conversation messages
            
        Returns:
            RAGResponse with answer, citations, and context IDs
        """
        try:
            # For now, use Gemini directly until you connect your RAG pipeline
            # TODO: Replace this with your actual RAG pipeline call
            # rag_result = your_rag_pipeline.generate_answer(question, context, conversation_history)
            
            # Use Gemini to generate a response
            gemini_response = self._generate_fallback_response(question, context, conversation_history)
            
            # Return Gemini response without mock citations
            # TODO: Replace with your actual RAG pipeline citations when ready
            return RAGResponse(
                answer_markdown=gemini_response.answer_markdown,
                citations=[],  # No mock citations - will be populated by your RAG pipeline
                image_citations=[],
                used_context_ids=[],  # No mock context IDs - will be populated by your RAG pipeline
                confident=True
            )
            
        except Exception as e:
            # Fallback to basic Gemini response if RAG fails
            return self._generate_fallback_response(question, context, conversation_history)
    
    def _generate_fallback_response(self, question: str, context: Dict[str, Any], conversation_history: List[Tuple[str, str]] = None) -> RAGResponse:
        """Generate fallback response using basic Gemini."""
        try:
            # Build system prompt
            system_prompt = "You are a scientific assistant specializing in space biology research. Answer concisely and factually. Do not invent citations."
            
            # Build messages list
            messages = [SystemMessage(content=system_prompt)]
            
            # Add conversation history
            if conversation_history:
                for role, content in conversation_history:
                    if role == "user":
                        messages.append(HumanMessage(content=content))
                    elif role == "assistant":
                        messages.append(AIMessage(content=content))
            
            # Add current question
            messages.append(HumanMessage(content=question))
            
            # Call Gemini
            response = self.llm.invoke(messages)
            answer_text = response.content if hasattr(response, 'content') else str(response)
            
            # Return as RAGResponse with no citations
            return RAGResponse(
                answer_markdown=answer_text,
                citations=[],
                image_citations=[],
                used_context_ids=[],
                confident=False
            )
            
        except Exception as e:
            # Ultimate fallback
            return RAGResponse(
                answer_markdown=f"I apologize, but I'm having trouble generating a response right now. Please try again later. Error: {str(e)}",
                citations=[],
                image_citations=[],
                used_context_ids=[],
                confident=False
            )


# Global RAG service instance
rag_service = RAGService()
