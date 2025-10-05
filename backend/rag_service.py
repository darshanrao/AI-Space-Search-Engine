"""
RAG Service - Interface to your RAG pipeline.
This integrates with the actual RAG pipeline for retrieval and generation.
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage

from models import RAGResponse, ImageCitation
from settings import settings
from generation.api import query_rag_json


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
        Generate RAG-powered answer using the actual RAG pipeline.
        
        Args:
            question: User's question
            context: Additional context (organism, focus area, etc.)
            conversation_history: Previous conversation messages
            
        Returns:
            RAGResponse with answer, citations, and context IDs
        """
        try:
            # Use the actual RAG pipeline
            rag_result = query_rag_json(question)
            
            # Convert RAG pipeline response to our RAGResponse format
            citations = rag_result.get("citations", [])  # Now just a list of URLs
            
            image_citations = []
            for img_citation in rag_result.get("image_citations", []):
                image_citations.append(ImageCitation(
                    id=img_citation.get("id", ""),
                    url=img_citation.get("url", ""),
                    why_relevant=img_citation.get("why_relevant", "")
                ))
            
            return RAGResponse(
                answer_markdown=rag_result.get("answer_markdown", ""),
                citations=citations,
                image_citations=image_citations,
                confidence_score=rag_result.get("confidence_score", 0)
            )
            
        except Exception as e:
            # Fallback to basic Gemini response if RAG fails
            print(f"RAG pipeline failed: {str(e)}")
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
                confidence_score=0
            )
            
        except Exception as e:
            # Ultimate fallback
            return RAGResponse(
                answer_markdown=f"I apologize, but I'm having trouble generating a response right now. Please try again later. Error: {str(e)}",
                citations=[],
                image_citations=[],
                confidence_score=0
            )


# Global RAG service instance
rag_service = RAGService()
