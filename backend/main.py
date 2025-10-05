"""
RAG-powered Space Bio Search Engine API.
Clean, simple FastAPI application designed for your RAG pipeline.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import uvicorn

from settings import settings
from routers import chat, scholar

# Create FastAPI app
app = FastAPI(
    title="RAG Space Bio Search Engine API",
    description="AI-powered search engine for space biology research with RAG pipeline integration",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(scholar.router, prefix="/api/scholar", tags=["scholar"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Space Bio Search Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "chat": "/api/chat",
            "session": "/api/session/{session_id}",
            "sessions": "/api/sessions",
            "scholar": "/api/scholar/search"
        }
    }


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )