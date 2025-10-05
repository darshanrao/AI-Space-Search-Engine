"""
RAG Chat API endpoints.
Clean, simple API designed specifically for your RAG pipeline.
"""

from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse, SessionResponse, HealthResponse
from rag_service import rag_service
from session_manager import session_manager
from datetime import datetime

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        service="rag-space-bio-api",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat()
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint - handles everything in one call.
    
    This is the primary endpoint your frontend will use.
    It handles session management, RAG processing, and response generation.
    """
    try:
        # Get or create session
        if request.session_id and session_manager.get_session(request.session_id):
            session_id = request.session_id
        else:
            session_id = session_manager.create_session(request.context)
        
        # Get conversation history
        conversation_history = session_manager.get_conversation_history(session_id)
        
        # Add user message to session
        session_manager.add_message(session_id, "user", request.message)
        
        # Generate RAG response
        rag_response = rag_service.generate_answer(
            question=request.message,
            context=session_manager.get_session(session_id)["context"],
            conversation_history=conversation_history
        )
        
        # Add assistant response to session
        session_manager.add_message(
            session_id, 
            "assistant", 
            rag_response.answer_markdown, 
            rag_response
        )
        
        return ChatResponse(
            session_id=session_id,
            message=rag_response.answer_markdown,
            rag_response=rag_response,
            context=session_manager.get_session(session_id)["context"],
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """Get session history and context."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    return SessionResponse(
        session_id=session_id,
        messages=session["messages"],
        context=session["context"],
        created_at=session["created_at"]
    )


@router.post("/session/{session_id}/context")
async def update_context(session_id: str, context: dict) -> dict:
    """Update session context."""
    try:
        session_manager.update_context(session_id, context)
        return {
            "session_id": session_id,
            "context": session_manager.get_session(session_id)["context"],
            "updated_at": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a session."""
    if session_manager.delete_session(session_id):
        return {
            "message": "Session deleted",
            "session_id": session_id
        }
    else:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )


@router.get("/sessions")
async def list_sessions() -> dict:
    """List all active sessions."""
    return {
        "sessions": session_manager.list_sessions(),
        "count": session_manager.get_session_count(),
        "timestamp": datetime.utcnow().isoformat()
    }