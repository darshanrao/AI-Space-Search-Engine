# Space Bio Search Engine Backend

A FastAPI backend for the Space Bio Search Engine, providing AI-powered chat functionality with Google Gemini and PostgreSQL.

## Features

- **Async FastAPI** with ORJSONResponse for high performance
- **Google Gemini Integration** via LangChain for AI chat
- **PostgreSQL Database** with async SQLAlchemy and Alembic migrations
- **Session-aware Chat** with conversation history
- **RAG (Retrieval-Augmented Generation)** for context-aware responses
- **CORS Support** for frontend integration
- **Comprehensive API** with health checks and paper search

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Add your GEMINI_API_KEY
# - Configure DATABASE_URL
# - Set ALLOW_ORIGINS for CORS
```

### 3. Database Setup

```bash
# Create database (PostgreSQL)
createdb space_bio

# Run migrations (when Alembic is configured)
alembic upgrade head
```

### 4. Run the Server

```bash
# Development mode
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Chat Endpoints
- `POST /api/thread` - Create new conversation thread
- `GET /api/thread/{id}` - Get thread with message history
- `PUT /api/thread/{id}/context` - Update thread context
- `POST /api/answer` - Generate AI answer with RAG
- `GET /api/thread/{id}/messages` - Get paginated messages

### Search Endpoints
- `POST /api/search` - Search research papers
- `GET /api/papers` - List available papers
- `GET /api/papers/{id}` - Get paper details
- `GET /api/papers/{id}/snippets` - Get paper snippets

### Utility Endpoints
- `GET /api/health` - Health check
- `GET /api/stats` - Service statistics

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── settings.py          # PydanticSettings configuration
├── db.py               # Database setup and session management
├── models.py           # SQLAlchemy database models
├── schemas.py          # Pydantic request/response schemas
├── chat_chain.py       # LangChain + Gemini integration
├── rag_hook.py         # RAG context retrieval (placeholder)
├── routers/
│   ├── chat.py         # Chat and thread endpoints
│   └── misc.py         # Health, search, and utility endpoints
├── requirements.txt    # Python dependencies
├── .env.example       # Environment configuration template
└── README.md          # This file
```

## Configuration

### Required Environment Variables

- `GEMINI_API_KEY` - Google Gemini API key
- `DATABASE_URL` - PostgreSQL connection string

### Optional Environment Variables

- `ALLOW_ORIGINS` - CORS allowed origins (default: localhost)
- `MODEL_NAME` - Gemini model name (default: gemini-1.5-flash)
- `DEBUG` - Debug mode (default: false)
- `MAX_RESPONSE_TOKENS` - Max AI response tokens (default: 800)

## Development

### Database Models

- **Thread**: Conversation sessions with context and metadata
- **Message**: Individual chat messages with role and content

### Key Components

- **ChatChain**: LangChain integration with conversation history
- **RAG Hook**: Context document retrieval (currently placeholder)
- **Async Session**: Database session management with dependency injection

### Adding New Endpoints

1. Create schema in `schemas.py`
2. Add route in appropriate router file
3. Implement business logic
4. Add tests (recommended)

## Production Deployment

1. Set `DEBUG=false` in environment
2. Configure production database
3. Set up proper CORS origins
4. Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
5. Set up monitoring and logging

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## License

MIT License - see LICENSE file for details.
