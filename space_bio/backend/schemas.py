"""
Pydantic schemas for request/response validation.
Defines data models for API endpoints matching frontend types.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


# Block types matching frontend
class Span(BaseModel):
    """Text span with highlighting information."""
    text: str
    start: int
    end: int
    type: Optional[str] = None


class ParagraphBlock(BaseModel):
    """Paragraph block with optional spans."""
    type: str = "paragraph"
    text: str
    spans: Optional[List[Span]] = None


class FigureBlock(BaseModel):
    """Figure block with caption and metadata."""
    type: str = "figure"
    caption: str
    figure_id: str
    figure_url: Optional[str] = None
    spans: Optional[List[Span]] = None


class TableBlock(BaseModel):
    """Table block with data and metadata."""
    type: str = "table"
    caption: Optional[str] = None
    table_id: str
    data: List[List[str]]
    spans: Optional[List[Span]] = None


# Union type for all block types
Block = Union[ParagraphBlock, FigureBlock, TableBlock]


class Citation(BaseModel):
    """Citation information for references."""
    id: str
    title: str
    authors: List[str]
    year: int
    venue: Optional[str] = None
    url: Optional[str] = None
    doi: Optional[str] = None


class EvidenceBadges(BaseModel):
    """Evidence type indicators."""
    has_figure: bool = False
    has_table: bool = False
    has_equation: bool = False
    has_code: bool = False


# Request schemas
class ThreadCreate(BaseModel):
    """Request to create a new thread."""
    seed_context: Optional[Dict[str, Any]] = None


class ThreadContextUpdate(BaseModel):
    """Request to update thread context."""
    context: Dict[str, Any]


class AnswerRequest(BaseModel):
    """Request for generating an answer."""
    q: str = Field(..., description="User question")
    thread_id: str = Field(..., description="Thread ID for context")
    k: Optional[int] = Field(default=8, description="Number of context documents")
    max_tokens: Optional[int] = Field(default=800, description="Maximum response tokens")


class SearchRequest(BaseModel):
    """Request for search functionality."""
    q: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    limit: int = Field(default=10, description="Number of results")
    offset: int = Field(default=0, description="Result offset")
    thread_id: Optional[str] = Field(None, description="Thread ID for context")


# Response schemas
class AnswerResponse(BaseModel):
    """Response for generated answer."""
    answer_id: str
    thread_id: str
    question: str
    answer: str  # The actual AI response text
    created_at: str
    evidence_badges: Optional[EvidenceBadges] = None
    blocks: List[Block]
    citations: List[Citation]
    graph: Optional[Dict[str, Any]] = None
    debug_topic: Optional[str] = None


class ThreadDTO(BaseModel):
    """Thread data transfer object."""
    thread_id: str
    messages: Optional[List[Dict[str, Any]]] = None
    context: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """Search results response."""
    hits: List[Dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    facets: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Database model schemas
class ThreadSchema(BaseModel):
    """Thread database model schema."""
    id: str
    created_at: datetime
    updated_at: datetime
    context: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class MessageSchema(BaseModel):
    """Message database model schema."""
    id: str
    thread_id: str
    role: str
    content: str
    created_at: datetime
    meta: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True
