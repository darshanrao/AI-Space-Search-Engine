"""
Session Manager - Handles conversation sessions and history.
Uses in-memory storage (can be replaced with Redis/database later).
"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Tuple
from models import ChatMessage, RAGResponse


class SessionManager:
    """Manages chat sessions and conversation history."""
    
    def __init__(self):
        # In-memory storage for sessions
        # In production, you might want to use Redis or a database
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, context: Dict[str, Any] = None) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "messages": [],
            "context": context or {},
            "created_at": datetime.utcnow().isoformat()
        }
        return session_id
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data."""
        return self.sessions.get(session_id)
    
    def add_message(self, session_id: str, role: str, content: str, rag_response: RAGResponse = None) -> None:
        """Add a message to the session."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        message = ChatMessage(
            role=role,
            content=content,
            rag_response=rag_response,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.sessions[session_id]["messages"].append(message)
    
    def get_conversation_history(self, session_id: str) -> List[Tuple[str, str]]:
        """Get conversation history as (role, content) tuples."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        history = []
        for msg in session["messages"]:
            history.append((msg.role, msg.content))
        
        return history
    
    def update_context(self, session_id: str, context: Dict[str, Any]) -> None:
        """Update session context."""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        self.sessions[session_id]["context"].update(context)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[str]:
        """List all session IDs."""
        return list(self.sessions.keys())
    
    def get_session_count(self) -> int:
        """Get total number of sessions."""
        return len(self.sessions)


# Global session manager instance
session_manager = SessionManager()
