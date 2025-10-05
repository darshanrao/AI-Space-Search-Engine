#!/bin/bash

# Start the AI Space Search Engine backend server

echo "🚀 Starting AI Space Search Engine Backend..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the server
echo "🌟 Starting FastAPI server..."
python run_server.py
