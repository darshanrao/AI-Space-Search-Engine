#!/usr/bin/env python3
"""
Debug session manager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from session_manager import session_manager
import uuid

def debug_session():
    print("Testing session manager...")
    
    # Create a session
    session_id = session_manager.create_session({"test": "context"})
    print(f"Created session: {session_id}")
    
    # Check if session exists
    session = session_manager.get_session(session_id)
    print(f"Retrieved session: {session is not None}")
    if session:
        print(f"Session data: {session}")
    
    # List all sessions
    sessions = session_manager.list_sessions()
    print(f"All sessions: {sessions}")
    
    # Add a message
    from models import RAGResponse, Citation
    mock_rag = RAGResponse(
        answer_markdown="Test response",
        citations=[Citation(id="test", url="http://test.com", why_relevant="test")],
        image_citations=[],
        used_context_ids=["test"],
        confident=True
    )
    
    session_manager.add_message(session_id, "user", "Test message")
    session_manager.add_message(session_id, "assistant", "Test response", mock_rag)
    
    # Check session again
    session = session_manager.get_session(session_id)
    print(f"Session after adding messages: {len(session['messages'])} messages")
    
    # Test conversation history
    history = session_manager.get_conversation_history(session_id)
    print(f"Conversation history: {history}")

if __name__ == "__main__":
    debug_session()

