"""
FastAPI server for the AI Space Search Engine backend.
Handles CORS and provides API endpoints for the frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from pathlib import Path

# Import the RAG pipeline
try:
    from generation.rag_pipeline import RAGPipeline
except ImportError:
    # Fallback if generation module isn't available
    RAGPipeline = None

app = FastAPI(title="AI Space Search Engine API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response models
class ThreadRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ThreadResponse(BaseModel):
    thread_id: str
    response: str
    success: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str

# Initialize RAG pipeline
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG pipeline on startup."""
    global rag_pipeline
    try:
        if RAGPipeline:
            rag_pipeline = RAGPipeline("nasa_corpus_v1", top_k=15, max_tokens=1000)
            print("✅ RAG Pipeline initialized successfully")
        else:
            print("⚠️  RAG Pipeline not available - generation module not found")
    except Exception as e:
        print(f"❌ Failed to initialize RAG Pipeline: {e}")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint for health check."""
    return HealthResponse(
        status="healthy",
        message="AI Space Search Engine API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="API is healthy and ready to serve requests"
    )

@app.post("/api/thread", response_model=ThreadResponse)
async def create_thread(request: ThreadRequest):
    """
    Create a new thread or continue an existing conversation.
    This endpoint handles the main chat functionality.
    """
    try:
        if not rag_pipeline:
            raise HTTPException(
                status_code=503,
                detail="RAG Pipeline not available. Please check backend configuration."
            )
        
        # Generate a simple thread ID if not provided
        thread_id = request.thread_id or f"thread_{hash(request.message) % 10000}"
        
        # Process the query using the RAG pipeline
        result = rag_pipeline.query(request.message)
        
        # Extract the answer from the result
        if isinstance(result, dict):
            answer = result.get("answer", "No answer generated")
        else:
            answer = str(result)
        
        return ThreadResponse(
            thread_id=thread_id,
            response=answer,
            success=True
        )
        
    except Exception as e:
        print(f"Error processing thread request: {e}")
        return ThreadResponse(
            thread_id=request.thread_id or "error",
            response="",
            success=False,
            error=str(e)
        )

@app.get("/api/search")
async def search(query: str, top_k: int = 10):
    """
    Search for documents without generating a response.
    Useful for debugging and testing retrieval.
    """
    try:
        if not rag_pipeline:
            raise HTTPException(
                status_code=503,
                detail="RAG Pipeline not available"
            )
        
        # Get retrieval results only
        docs = rag_pipeline.get_retrieval_only(query, top_k)
        
        return {
            "query": query,
            "results": docs,
            "count": len(docs),
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
