# RAG Space Bio Search Engine Backend

A clean, streamlined FastAPI backend designed specifically for your RAG pipeline integration.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env with your actual values
# At minimum, set your GEMINI_API_KEY
```

### 3. Run the Server
```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### Main Chat Endpoint
```http
POST /api/chat
```

**Request:**
```json
{
  "message": "What genes are implicated in bisphosphonate-mediated muscle improvements?",
  "session_id": "optional-existing-session-id",
  "context": {
    "organism": "C. elegans",
    "focus": "muscle health"
  }
}
```

**Response:**
```json
{
  "session_id": "uuid-session-id",
  "message": "Genes implicated in bisphosphonate-mediated muscle improvements include...",
  "rag_response": {
    "answer_markdown": "Genes implicated in bisphosphonate-mediated muscle improvements include farnesyl diphosphate synthetase (fdps-1/FDPS)...",
    "citations": [
      {
        "id": "PMC10751425:discussion:7b0f4426",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10751425/",
        "why_relevant": "Identifies bisphosphonates' role in muscle health..."
      }
    ],
    "image_citations": [],
    "used_context_ids": ["925cb1d1-e4ee-54a3-ab19-1a0e09abdd9f"],
    "confident": true
  },
  "context": {"organism": "C. elegans"},
  "timestamp": "2025-10-04T22:53:00.000000"
}
```

### Session Management
```http
GET /api/session/{session_id}     # Get conversation history
POST /api/session/{session_id}/context  # Update context
DELETE /api/session/{session_id}  # Delete session
GET /api/sessions                 # List all sessions
```

### Health Check
```http
GET /api/health
```

## 🔧 RAG Pipeline Integration

### Connect Your RAG Pipeline

Edit `rag_service.py` and replace the `generate_answer` method:

```python
def generate_answer(self, question: str, context: Dict[str, Any], conversation_history: List[Tuple[str, str]] = None) -> RAGResponse:
    """
    Generate RAG-powered answer.
    Replace this with your actual RAG pipeline call.
    """
    # Call your RAG pipeline
    rag_result = your_rag_pipeline.generate_answer(question, context, conversation_history)
    
    # Convert to RAGResponse format
    return RAGResponse(
        answer_markdown=rag_result["answer_markdown"],
        citations=[
            Citation(
                id=citation["id"],
                url=citation["url"],
                why_relevant=citation["why_relevant"]
            ) for citation in rag_result["citations"]
        ],
        image_citations=[
            ImageCitation(
                id=img["id"],
                url=img["url"],
                why_relevant=img["why_relevant"]
            ) for img in rag_result.get("image_citations", [])
        ],
        used_context_ids=rag_result["used_context_ids"],
        confident=rag_result["confident"]
    )
```

## 🧪 Testing

Run the test script:
```bash
python test_api.py
```

## 🎯 Key Features

- ✅ **Single API Call**: One endpoint for complete chat functionality
- ✅ **Session Management**: Automatic session handling with conversation history
- ✅ **RAG Integration**: Ready for your RAG pipeline integration
- ✅ **Citation Support**: Full support for citations and context IDs
- ✅ **Fallback System**: Falls back to basic Gemini if RAG fails
- ✅ **CORS Enabled**: Ready for frontend integration
- ✅ **No Database**: Uses in-memory storage (can be upgraded later)

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI application
├── settings.py             # Configuration settings
├── models.py               # Pydantic models
├── rag_service.py          # RAG pipeline interface
├── session_manager.py      # Session management
├── routers/
│   ├── __init__.py
│   └── chat.py            # Chat API endpoints
├── requirements.txt        # Dependencies
├── test_api.py            # Test script
├── env_example.txt        # Environment configuration example
└── README.md              # This file
```

## 🔄 Frontend Integration

### Simple Usage
```javascript
// Send a message
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "What genes are implicated in bisphosphonate-mediated muscle improvements?",
    context: { organism: "C. elegans" }
  })
});

const data = await response.json();
console.log(data.message); // AI response
console.log(data.rag_response.citations); // Citations array
```

### React Component Example
```jsx
function RAGChatComponent() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  const sendMessage = async (message) => {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        context: { organism: "C. elegans" }
      })
    });

    const data = await response.json();
    setSessionId(data.session_id);
    
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: data.message,
      citations: data.rag_response?.citations || []
    }]);
  };

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i}>
          <p>{msg.content}</p>
          {msg.citations.map((citation, j) => (
            <a key={j} href={citation.url}>{citation.id}</a>
          ))}
        </div>
      ))}
    </div>
  );
}
```

## 🚀 Next Steps

1. **Set up your environment**: Copy `env_example.txt` to `.env` and add your Gemini API key
2. **Connect your RAG pipeline**: Edit `rag_service.py` to integrate with your actual RAG system
3. **Test the API**: Run `python test_api.py` to verify everything works
4. **Update your frontend**: Use the new `/api/chat` endpoint instead of the old complex flow
5. **Deploy and enjoy**: Your RAG-powered chatbot is ready!

This backend is designed to be simple, reliable, and perfectly matched to your RAG pipeline format. No more complex multi-endpoint flows - just one clean API call for everything! 🎉
