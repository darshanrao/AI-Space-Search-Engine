#!/usr/bin/env python3
"""
Script to run the FastAPI server for the AI Space Search Engine.
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    # Load environment variables from .env file
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"Loading environment variables from {env_path}")
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
