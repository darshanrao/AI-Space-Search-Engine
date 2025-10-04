"""
Chat API endpoints for thread management and message handling.
Provides endpoints for creating threads, managing context, and generating answers.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from db import DatabaseSession, SessionLocal
from models import Thread, Message
from schemas import (
    ThreadCreate, 
    ThreadDTO, 
    ThreadContextUpdate,
    AnswerRequest,
    AnswerResponse
)
from chat_chain import run_chat_turn
from settings import settings

router = APIRouter()


@router.post("/thread", response_model=ThreadDTO)
def create_thread(
    request: ThreadCreate,
    session: Session = DatabaseSession
) -> ThreadDTO:
    """
    Create a new conversation thread.
    
    Args:
        request: Thread creation request with optional seed context
        session: Database session
        
    Returns:
        Created thread information
    """
    # Generate unique thread ID
    thread_id = str(uuid.uuid4())
    
    # Create thread in database
    thread = Thread(
        id=thread_id,
        title=None,
        context=request.seed_context or {}
    )
    
    session.add(thread)
    session.commit()
    session.refresh(thread)
    
    return ThreadDTO(
        thread_id=thread_id,
        messages=[],
        context=thread.context
    )


@router.get("/thread/{thread_id}", response_model=ThreadDTO)
def get_thread(
    thread_id: str,
    session: Session = DatabaseSession
) -> ThreadDTO:
    """
    Get thread information and message history.
    
    Args:
        thread_id: Thread identifier
        session: Database session
        
    Returns:
        Thread information with messages
    """
    # Query thread with messages
    stmt = select(Thread).where(Thread.id == thread_id)
    result = session.execute(stmt)
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Format messages for response
    messages = []
    for msg in thread.messages:
        message_data = {
            "role": msg.role,
            "text": msg.content if msg.role == "user" else None,
            "answer": msg.content if msg.role == "assistant" else None
        }
        messages.append(message_data)
    
    return ThreadDTO(
        thread_id=thread_id,
        messages=messages,
        context=thread.context
    )


@router.put("/thread/{thread_id}/context", response_model=ThreadDTO)
def update_thread_context(
    thread_id: str,
    request: ThreadContextUpdate,
    session: Session = DatabaseSession
) -> ThreadDTO:
    """
    Update thread context (organism, conditions, etc.).
    
    Args:
        thread_id: Thread identifier
        request: Context update request
        session: Database session
        
    Returns:
        Updated thread information
    """
    # Query thread
    stmt = select(Thread).where(Thread.id == thread_id)
    result = session.execute(stmt)
    thread = result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Update context
    if thread.context is None:
        thread.context = {}
    
    # Merge the new context with existing context
    thread.context.update(request.context)
    
    # Update timestamp
    thread.updated_at = datetime.utcnow()
    
    session.commit()
    session.refresh(thread)
    
    return ThreadDTO(
        thread_id=thread_id,
        context=thread.context
    )


@router.post("/answer", response_model=AnswerResponse)
def generate_answer(
    request: AnswerRequest,
    session: Session = DatabaseSession
) -> AnswerResponse:
    """
    Generate AI answer for a user question with RAG context.
    
    Args:
        request: Answer generation request
        session: Database session
        
    Returns:
        Generated answer with blocks, citations, and metadata
    """
    # Verify thread exists
    thread_stmt = select(Thread).where(Thread.id == request.thread_id)
    thread_result = session.execute(thread_stmt)
    thread = thread_result.scalar_one_or_none()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Store user message in database
    user_message = Message(
        id=str(uuid.uuid4()),
        thread_id=request.thread_id,
        role="user",
        content=request.q,
        meta={}
    )
    session.add(user_message)
    
    # Generate AI response using chat chain
    try:
        # Generate answer using the new chat_chain function
        assistant_text = run_chat_turn(
            question=request.q,
            thread_id=request.thread_id,
            context=thread.context,
            settings=settings,
            session=session
        )
        
        # Store assistant message in database
        assistant_message = Message(
            id=str(uuid.uuid4()),
            thread_id=request.thread_id,
            role="assistant",
            content=assistant_text,
            meta={}
        )
        session.add(assistant_message)
        
        # Commit both messages
        session.commit()
        
        # Return response in the new format
        return AnswerResponse(
            answer_id=assistant_message.id,
            thread_id=request.thread_id,
            question=request.q,
            answer=assistant_text,  # Include the actual AI response
            created_at=assistant_message.created_at.isoformat(),
            evidence_badges=None,
            blocks=[],
            citations=[],
            graph=None,
            debug_topic=None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate answer: {str(e)}"
        )


