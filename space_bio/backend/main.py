"""
FastAPI application for Space Bio Search Engine backend.
Provides async API endpoints for chat, search, and research functionality.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
import uvicorn

from settings import settings
from routers import chat, misc

# Create FastAPI app with ORJSONResponse as default
app = FastAPI(
    title="Space Bio Search Engine API",
    description="AI-powered search engine for space biology research",
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
app.include_router(misc.router, prefix="/api", tags=["misc"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Space Bio Search Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "space-bio-api",
        "version": "1.0.0"
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
