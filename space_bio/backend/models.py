"""
Pydantic models for RAG Chat API.
Matches your RAG pipeline response format exactly.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class Citation(BaseModel):
    """Citation model matching your RAG pipeline format."""
    id: str
    url: str
    why_relevant: str


class ImageCitation(BaseModel):
    """Image citation model."""
    id: str
    url: str
    why_relevant: str


class RAGResponse(BaseModel):
    """RAG response model matching your pipeline output exactly."""
    answer_markdown: str
    citations: List[Citation]
    image_citations: List[ImageCitation]
    used_context_ids: List[str]
    confident: bool


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: str  # "user" or "assistant"
    content: str
    rag_response: Optional[RAGResponse] = None
    timestamp: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: Optional[str] = None
    context: Dict[str, Any] = {}


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    session_id: str
    message: str
    rag_response: Optional[RAGResponse] = None
    context: Dict[str, Any]
    timestamp: str


class SessionResponse(BaseModel):
    """Response model for session history."""
    session_id: str
    messages: List[ChatMessage]
    context: Dict[str, Any]
    created_at: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: str
