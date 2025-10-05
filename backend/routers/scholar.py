"""
Google Scholar API endpoints.
Provides academic paper search functionality via SerpApi.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from generation.scholar_tool import scholar_search_tool
from datetime import datetime

router = APIRouter()


class ScholarSearchRequest(BaseModel):
    """Request model for Google Scholar search."""
    query: Optional[str] = None
    context: Optional[str] = None
    num_results: Optional[int] = 5


class ScholarSearchResponse(BaseModel):
    """Response model for Google Scholar search."""
    query: str
    results: str
    num_results: int
    timestamp: str


@router.post("/search", response_model=ScholarSearchResponse)
async def search_scholar(request: ScholarSearchRequest) -> ScholarSearchResponse:
    """
    Search Google Scholar for academic papers.
    
    Args:
        request: Search request with query and optional result count
        
    Returns:
        ScholarSearchResponse with formatted results
    """
    try:
        # Determine search query from context or explicit query
        search_query = None
        
        if request.query and request.query.strip():
            search_query = request.query.strip()
        elif request.context and request.context.strip():
            # Use context to generate a search query
            search_query = request.context.strip()
        else:
            raise HTTPException(
                status_code=400,
                detail="Either query or context must be provided"
            )
        
        # Limit results to reasonable number
        num_results = min(max(request.num_results or 5, 1), 20)
        
        # Perform the search using context-aware method if context is provided
        if request.context and request.context.strip():
            generated_query, results = scholar_search_tool.search_with_context(
                conversation_context=request.context,
                user_query=request.query,
                num_results=num_results
            )
            actual_query = generated_query
        else:
            # Use direct search for explicit queries
            results = scholar_search_tool._run(search_query, num_results)
            actual_query = search_query
        
        return ScholarSearchResponse(
            query=actual_query,
            results=results,
            num_results=num_results,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scholar search failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for Google Scholar service."""
    return {
        "status": "healthy",
        "service": "google-scholar-api",
        "timestamp": datetime.utcnow().isoformat(),
        "api_configured": bool(scholar_search_tool.api_key)
    }
