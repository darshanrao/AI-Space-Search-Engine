"""
Database models for the Space Bio Search Engine.
Defines Thread and Message models with JSONB fields for flexible data storage.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from db import Base


class Thread(Base):
    """Thread model representing a conversation session."""
    
    __tablename__ = "threads"
    
    # Primary key - UUID4 string
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Timestamp with timezone, default now
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    
    # Updated timestamp
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    
    # Optional title
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Context as JSONB with default empty dict
    context: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict,
        nullable=False
    )
    
    # Relationships
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="thread",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )


class Message(Base):
    """Message model representing individual chat messages."""
    
    __tablename__ = "messages"
    
    # Primary key
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to thread
    thread_id: Mapped[str] = mapped_column(
        String, 
        ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Message role
    role: Mapped[str] = mapped_column(String, nullable=False)
    
    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamp with timezone, default now
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.utcnow,
        nullable=False
    )
    
    # Meta as JSONB with default empty dict
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict,
        nullable=False
    )
    
    # Relationships
    thread: Mapped["Thread"] = relationship("Thread", back_populates="messages")


# Index on Message(thread_id, created_at) for efficient querying
Index('ix_messages_thread_id_created_at', Message.thread_id, Message.created_at)
