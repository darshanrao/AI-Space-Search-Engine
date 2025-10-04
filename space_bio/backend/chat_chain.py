"""
LangChain integration with Google Gemini for chat functionality.
Provides session-aware chat chains with conversation history from database.
"""

import time
import logging
from typing import List, Dict, Any, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from sqlalchemy.orm import Session
from sqlalchemy import select

from models import Message

# Set up logging
logger = logging.getLogger(__name__)


def build_system_prompt(context: Dict[str, Any]) -> str:
    """
    Build system prompt for the scientific assistant.
    
    Args:
        context: Thread context dictionary
        
    Returns:
        System prompt string
    """
    return "You are a scientific assistant. Answer concisely and factually. Do not invent citations."


def get_history(session: Session, thread_id: str) -> List[Tuple[str, str]]:
    """
    Get conversation history from database.
    
    Args:
        session: Database session
        thread_id: Thread ID to get history for
        
    Returns:
        List of (role, content) tuples ordered by created_at
    """
    try:
        # Query messages for the thread ordered by creation time
        stmt = select(Message).where(
            Message.thread_id == thread_id
        ).order_by(Message.created_at.asc())
        
        result = session.execute(stmt)
        messages = result.scalars().all()
        
        # Convert to list of (role, content) tuples
        history = []
        for msg in messages:
            history.append((msg.role, msg.content))
        
        return history
    except Exception as e:
        # If database query fails (e.g., tables don't exist), return empty history
        logger.warning(f"Could not retrieve history for thread {thread_id}: {e}")
        return []


def run_chat_turn(
    question: str, 
    thread_id: str, 
    context: Dict[str, Any], 
    settings, 
    session: Session
) -> str:
    """
    Run a single chat turn with Gemini.
    
    Args:
        question: User's question
        thread_id: Thread ID for context
        context: Thread context dictionary
        settings: Application settings
        session: Database session
        
    Returns:
        Assistant response text
    """
    start_time = time.time()
    logger.info(f"Starting chat turn for thread {thread_id}")
    
    try:
        # Initialize Gemini model with LangChain
        llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7,
            max_output_tokens=settings.MAX_RESPONSE_TOKENS
        )
        
        # Build system prompt
        system_prompt = build_system_prompt(context)
        
        # Get conversation history
        history = get_history(session, thread_id)
        logger.info(f"Retrieved {len(history)} messages from history")
        
        # Build messages list
        messages = [SystemMessage(content=system_prompt)]
        
        # Add history messages
        for role, content in history:
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        
        # Add current user question
        messages.append(HumanMessage(content=question))
        
        # Call Gemini
        logger.info(f"Calling Gemini with {len(messages)} messages")
        response = llm.invoke(messages)
        
        # Extract response text
        assistant_text = response.content if hasattr(response, 'content') else str(response)
        
        # Log timing
        elapsed_time = time.time() - start_time
        logger.info(f"Chat turn completed in {elapsed_time:.2f}s")
        
        return assistant_text
        
    except Exception as e:
        logger.error(f"Error in chat turn: {str(e)}")
        raise
