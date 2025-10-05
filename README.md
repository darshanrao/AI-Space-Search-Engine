# AI Space Research Search Engine

A Retrieval-Augmented Generation (RAG) system for querying and synthesizing information from NASA's bioscience research publications. Built with hybrid vector search, agentic reasoning, and modern web technologies.

## Overview

This system processes 608 NASA bioscience publications from PubMed Central and provides an intelligent conversational interface for exploring space biology research. The system uses hybrid dense+sparse vector retrieval, a LangChain ReAct agent for intelligent query handling, and Google Gemini for answer generation with inline citations.

### Key Features

- **Hybrid Retrieval**: Combines dense (semantic) and sparse (keyword) embeddings using Reciprocal Rank Fusion
- **Agentic RAG**: LangChain ReAct agent that reasons about when to search vs. use base knowledge
- **Citation System**: All answers include inline citations linking to specific PMC article sections
- **Session Management**: Maintains conversation history and context across queries
- **Context Filtering**: Filter by organism, research focus, and other metadata
- **Multi-modal Support**: Retrieves and cites both text and scientific figures
- **Validated Performance**: Evaluated on 181 test cases with 72% overall accuracy, 83% answer quality

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  • Chat Interface  • Source Viewer  • Session Management        │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
┌────────────────────────────┴────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │ Chat Router  │  │   Session    │  │   Image Search       │ │
│  │              │──│   Manager    │  │   Service            │ │
│  └──────┬───────┘  └──────────────┘  └──────────────────────┘ │
│         │                                                        │
│  ┌──────┴─────────────────────────────────────────────────┐   │
│  │              Agent Service (LangChain ReAct)            │   │
│  │  • Question Analysis  • Tool Selection  • Synthesis    │   │
│  └──────┬─────────────────────────────────────────────────┘   │
│         │                                                        │
│  ┌──────┴────────────────────────┐                             │
│  │      RAG Tool                 │                              │
│  │  ┌────────────┐  ┌──────────┐ │                             │
│  │  │ Retrieval  │  │  Gemini  │ │                             │
│  │  │  Client    │  │  Client  │ │                             │
│  │  └─────┬──────┘  └────┬─────┘ │                             │
│  └────────┼──────────────┼───────┘                             │
└───────────┼──────────────┼─────────────────────────────────────┘
            │              │
    ┌───────┴──────┐  ┌───┴──────────┐
    │   Qdrant     │  │   Google     │
    │   Cloud      │  │   Gemini API │
    │  (Vectors)   │  │              │
    └──────────────┘  └──────────────┘
```

### Data Flow

1. **User Query** → Frontend sends question + context to `/api/chat`
2. **Agent Analysis** → ReAct agent determines if RAG search is needed
3. **Hybrid Retrieval** → If needed, queries Qdrant with dense + sparse vectors
4. **RRF Fusion** → Combines dense and sparse results using Reciprocal Rank Fusion
5. **Answer Generation** → Gemini synthesizes answer from top-15 chunks
6. **Citation Extraction** → Formats inline citations with PMC IDs and relevance
7. **Response** → Streams formatted answer with citations back to frontend

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **Qdrant Cloud Account**: For vector storage (or local Qdrant instance)
- **Google Gemini API Key**: For LLM generation

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd AI-Space-Search-Engine
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env_template.txt .env
# Edit .env and add:
#   GEMINI_API_KEY=your-gemini-api-key
#   QDRANT_URL=https://your-cluster.cloud.qdrant.io
#   QDRANT_API_KEY=your-qdrant-api-key
```

### 3. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Frontend runs on http://localhost:3000
# Backend API is expected at http://localhost:8000
```

### 4. Data Setup (Required)

**Important:** The application requires the 608 NASA bioscience papers to be indexed in your Qdrant collection.

**Option A: Use Pre-populated Qdrant Collection**
If you have access to an existing Qdrant collection with the indexed papers, simply configure the correct `QDRANT_URL` and `COLLECTION_NAME` in your `.env` file.

**Option B: Index Papers Yourself**
If you need to populate the collection from scratch:

1. Obtain the 608 NASA bioscience papers (XML format from PubMed Central)
2. Process papers into semantic chunks by section (Abstract, Methods, Results, Discussion)
3. Generate embeddings:
   - Dense: `sentence-transformers/all-MiniLM-L6-v2`
   - Sparse: `prithivida/Splade_PP_en_v1`
4. Upload to Qdrant with metadata schema:
   ```python
   {
       "id": "PMC12345:results:uuid",
       "pmc_id": "PMC12345",
       "section": "results",
       "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12345/",
       "text": "chunk content...",
       "publication_date": "2024-01-15"
   }
   ```

**Note:** Data processing scripts are not included in this repository. Contact the project maintainers for access to the preprocessed dataset or ingestion pipeline.

## Project Structure

```
AI-Space-Search-Engine/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── settings.py                # Configuration management
│   ├── models.py                  # Pydantic data models
│   ├── rag_service.py             # RAG service wrapper
│   ├── session_manager.py         # Session/conversation management
│   ├── image_search_service.py    # Scientific image retrieval
│   ├── routers/
│   │   ├── chat.py                # Chat API endpoints
│   │   └── scholar.py             # Google Scholar search endpoints
│   ├── generation/
│   │   ├── agent_service.py       # LangChain ReAct agent
│   │   ├── rag_pipeline.py        # RAG orchestration
│   │   ├── rag_tool.py            # RAG tool for agent
│   │   ├── scholar_tool.py        # Google Scholar search tool
│   │   ├── query_generator.py     # LLM-based query generator for Scholar
│   │   ├── retrieval_client.py    # Qdrant hybrid search client
│   │   ├── gemini_client.py       # Google Gemini API client
│   │   ├── api.py                 # Standalone RAG API functions
│   │   └── cli.py                 # Command-line interface
│   └── retrieval/
│       └── query_cli.py           # Standalone retrieval testing
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx         # Root layout
│   │   │   ├── page.tsx           # Main chat page
│   │   │   └── thread/[id]/       # Individual session view
│   │   ├── components/
│   │   │   ├── ChatAnswer.tsx     # Answer display with citations
│   │   │   ├── AnswerCard.tsx     # Individual answer card
│   │   │   ├── SearchBar.tsx      # Query input
│   │   │   ├── SourcesViewer.tsx  # Retrieved chunks viewer
│   │   │   ├── SourcesDrawer.tsx  # Tabbed paper viewer drawer
│   │   │   ├── SessionsSidebar.tsx # Conversation history
│   │   │   ├── ImageSidebar.tsx   # Image citations
│   │   │   ├── ContextChips.tsx   # Active filters display
│   │   │   └── MiniGraphPanel.tsx # Knowledge graph viz
│   │   └── lib/
│   │       ├── api.ts             # Backend API client
│   │       └── types.ts           # TypeScript type definitions
│   └── package.json
├── evaluation/
│   ├── evaluator.py               # Core evaluation metrics calculator
│   ├── run_evaluation.py          # Main evaluation orchestration script
│   ├── generate_test_cases.py     # Test case generation utilities
│   ├── stratified_sampling.py     # Sampling strategy for test selection
│   ├── find_best_questions.py     # Results analysis script
│   ├── data/
│   │   ├── test_set/              # Test case JSON files by article
│   │   ├── formatted_docs/        # Ground truth document chunks
│   │   └── rag_outputs/           # Cached RAG responses
│   ├── results/                   # Evaluation results (181 cases)
│   ├── PRESENTATION_METRICS.md    # Evaluation summary
│   └── BEST_RAG_RESULTS.md        # Top performing examples
├── .env                           # Environment configuration (not in git)
└── README.md                      # This file
```

## Components

### Backend Components

#### 1. Agent Service (`generation/agent_service.py`)

LangChain ReAct agent that intelligently decides when to use RAG vs. base knowledge.

**Features:**
- Custom prompt template for space biology domain
- Tool calling with RAG search tool
- Conversation history integration
- Error handling and parsing

**Agent Flow:**
```
Question → Thought → Action (search/answer) → Observation → Final Answer
```

#### 2. RAG Pipeline (`generation/rag_pipeline.py`)

Orchestrates retrieval and generation.

**Process:**
1. Query Qdrant with hybrid search (top-15 chunks)
2. Format context from retrieved chunks
3. Call Gemini with structured prompt
4. Parse citations from response
5. Return formatted RAGResponse

**Configuration:**
- `collection_name`: Qdrant collection (default: `nasa_corpus_v1`)
- `top_k`: Number of chunks to retrieve (default: 15)
- `max_tokens`: Gemini output limit

#### 3. Retrieval Client (`generation/retrieval_client.py`)

Handles hybrid vector search using Qdrant.

**Search Strategy:**
- Dense vectors: `sentence-transformers/all-MiniLM-L6-v2`
- Sparse vectors: `prithivida/Splade_PP_en_v1`
- Fusion: Reciprocal Rank Fusion (RRF)

**Metadata Fields:**
- `id`: Chunk citation ID (e.g., `PMC10751425:discussion:7b0f4426`)
- `section`: Document section (abstract, methods, results, discussion)
- `url`: PubMed Central article URL
- `pmc_id`: Article identifier
- `text`: Chunk content

#### 4. Gemini Client (`generation/gemini_client.py`)

Manages Google Gemini API integration.

**Responsibilities:**
- Prompt construction with retrieved context
- API error handling and retries
- Response parsing and validation
- Citation extraction

#### 5. Session Manager (`session_manager.py`)

In-memory conversation storage (can be replaced with database).

**Features:**
- Create/retrieve/update/delete sessions
- Conversation history tracking
- Context persistence (organism, focus area)
- Timestamp management

#### 6. Image Search Service (`image_search_service.py`)

Retrieves scientific figures from papers using SerpAPI.

**Capabilities:**
- Google Images search for scientific diagrams
- PMC-specific image retrieval
- Result filtering and ranking

#### 7. Scholar Search Tool (`generation/scholar_tool.py`)

LangChain tool for searching Google Scholar academic papers.

**Features:**
- SerpAPI integration for Google Scholar search
- Configurable result limit (1-20 papers)
- Context-aware search using LLM-generated queries
- Formatted results with titles and links

**Usage:**
```python
# Direct search
results = scholar_search_tool._run("microgravity muscle atrophy", num_results=5)

# Context-aware search
query, results = scholar_search_tool.search_with_context(
    conversation_context="User asked about muscle loss in space",
    user_query="recent papers",
    num_results=5
)
```

#### 8. Query Generator (`generation/query_generator.py`)

LLM-powered service for generating optimized Google Scholar queries.

**Process:**
1. Analyzes conversation context and user intent
2. Uses Gemini to generate focused academic search query
3. Extracts key terms (organisms, processes, conditions)
4. Fallback to rule-based extraction if LLM fails

**Example:**
- Input: "What are the effects of space on muscles?"
- Output: "microgravity muscle atrophy space biology"

#### 9. Scholar Router (`routers/scholar.py`)

FastAPI router for Google Scholar search endpoints.

**Endpoints:**
- `POST /api/scholar/search`: Search academic papers
- `GET /api/scholar/health`: Service health check

### Frontend Components

#### 1. Chat Interface (`app/page.tsx`)

Main application entry point.

**Features:**
- Real-time message streaming
- Session creation and management
- Context chip integration
- Auto-scroll to latest message

#### 2. Answer Card (`components/AnswerCard.tsx`)

Displays formatted answers with inline citations.

**Rendering:**
- Markdown parsing
- Citation number formatting `[1]`, `[2]`
- Citation hover/click interactions
- Copy to clipboard

#### 3. Sources Viewer (`components/SourcesViewer.tsx`)

Expandable panel showing all retrieved chunks.

**Display:**
- Chunk relevance scores
- Source document metadata
- Full text content
- Citation IDs

#### 4. Sources Drawer (`components/SourcesDrawer.tsx`)

Tabbed drawer for viewing paper sources in an iframe.

**Features:**
- Opens papers in sidebar tabs from citation clicks
- Multiple tab support with tab management
- Embedded paper viewer using iframes
- Fallback to external links if iframe fails
- Toggle button with active tab count

#### 5. Sessions Sidebar (`components/SessionsSidebar.tsx`)

Navigation for conversation history.

**Features:**
- List all sessions
- Create new session
- Delete sessions
- Highlight active session

### Evaluation Components

#### 1. Evaluator (`evaluation/evaluator.py`)

Core metrics calculation engine.

**Metrics Implemented:**
- **Retrieval**: Strict recall (must-retrieve), soft recall (must + should retrieve)
- **Answer Quality**: Semantic similarity (cosine), key facts coverage
- **Citations**: Precision, recall, format accuracy
- **Overall Score**: Weighted combination (35% retrieval, 45% answer, 20% citation)

**Dependencies:**
- `sentence-transformers` for semantic similarity
- `scikit-learn` for cosine similarity calculation

#### 2. Evaluation Runner (`evaluation/run_evaluation.py`)

Orchestrates the full evaluation pipeline.

**Process:**
1. Load test cases from `data/test_set/article_{id}_test_cases.json`
2. Query RAG system via `backend.generation.api.query_rag_debug`
3. Parse RAG outputs to extract answer, citations, and chunks
4. Compare against ground truth from test cases
5. Calculate all metrics using `RAGEvaluator`
6. Save results to `results/` directory

**Features:**
- Caching of RAG outputs to avoid re-querying
- Per-article and aggregate result generation
- Progress tracking and error handling
- Command-line arguments for selective evaluation

#### 3. Test Case Generator (`evaluation/generate_test_cases.py`)

Utility for creating new test cases.

**Capabilities:**
- Generate questions of different types (factual, comparative, complex, specific, broad)
- Specify difficulty levels (easy, medium, hard)
- Define ground truth answers and required citations
- Format test cases in standard JSON schema

#### 4. Results Analyzer (`evaluation/find_best_questions.py`)

Post-evaluation analysis tool.

**Functions:**
- Parses all result JSONs
- Sorts by overall score
- Identifies top performers by question type
- Finds diverse exemplar questions for presentations

## Running the Application

**Prerequisites:** Ensure you have completed all installation steps, including configuring `.env` and setting up your Qdrant collection with data (see Installation section above).

### Start Backend

```bash
cd backend
source venv/bin/activate
python main.py
```

Backend runs at `http://localhost:8000`

**API Documentation:**
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Verify Backend is Running:**
```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Should return: {"status":"healthy"}
```

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at `http://localhost:3000`

### Testing RAG Pipeline Directly

```bash
# Test retrieval only
cd backend
PYTHONPATH=$PWD python -m retrieval.query_cli \
  --collection nasa_corpus_v1 \
  --query "What are microgravity effects on stem cells?" \
  --top-k 15

# Test full RAG pipeline
PYTHONPATH=$PWD python -m generation.cli \
  --question "What are microgravity effects on stem cells?" \
  --top-k 15
```

## API Documentation

### POST /api/chat

Main endpoint for conversational RAG queries.

**Request:**
```json
{
  "message": "What genes are implicated in bisphosphonate-mediated muscle improvements?",
  "session_id": "optional-uuid",
  "context": {
    "organism": "C. elegans",
    "focus": "muscle health"
  }
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "message": "Generated answer with citations...",
  "rag_response": {
    "answer_markdown": "Full answer with [1], [2] citations...",
    "citations": [
      {
        "id": "PMC10751425:discussion:7b0f4426",
        "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10751425/",
        "why_relevant": "Identifies bisphosphonates' role..."
      }
    ],
    "image_citations": [],
    "used_context_ids": ["chunk-id-1", "chunk-id-2"],
    "confident": true
  },
  "context": {"organism": "C. elegans"},
  "timestamp": "2025-10-04T22:53:00.000000"
}
```

### GET /api/session/{session_id}

Retrieve conversation history.

**Response:**
```json
{
  "session_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "What genes...",
      "timestamp": "2025-10-04T22:53:00"
    },
    {
      "role": "assistant",
      "content": "The primary gene is...",
      "rag_response": {...},
      "timestamp": "2025-10-04T22:53:05"
    }
  ],
  "context": {"organism": "C. elegans"}
}
```

### GET /api/sessions

List all active sessions.

### DELETE /api/session/{session_id}

Delete a session and its history.

### POST /api/session/{session_id}/context

Update session context filters.

**Request:**
```json
{
  "organism": "Mouse",
  "focus": "bone density"
}
```

### POST /api/scholar/search

Search Google Scholar for academic papers.

**Request:**
```json
{
  "query": "microgravity muscle atrophy",
  "context": "User asked about muscle loss in space",
  "num_results": 5
}
```

**Response:**
```json
{
  "query": "microgravity muscle atrophy space biology",
  "results": "🔍 Google Scholar Results for: 'microgravity muscle atrophy space biology'\n\n📄 Paper #1\nTitle: Effects of microgravity on muscle development\n🔗 Link: https://scholar.google.com/...\n\n...",
  "num_results": 5,
  "timestamp": "2025-10-05T10:00:00.000000"
}
```

### GET /api/scholar/health

Health check for Google Scholar service.

**Response:**
```json
{
  "status": "healthy",
  "service": "google-scholar-api",
  "timestamp": "2025-10-05T10:00:00.000000",
  "api_configured": true
}
```

## Evaluation & Testing

The system was rigorously evaluated on 181 test cases across 42 research articles to measure performance across different question types and difficulty levels.

### Evaluation Methodology

**Test Dataset:**
- 181 questions covering 5 types (Factual, Comparative, Complex, Specific, Broad)
- 3 difficulty levels (Easy, Medium, Hard)
- Human-verified ground truth answers
- Questions designed to test retrieval, answer quality, and citation accuracy

**Evaluation Process:**
1. System generates answer for each test question
2. Retrieval quality scored against expected relevant papers
3. Answer quality measured via semantic similarity and key facts coverage
4. Citations validated for precision, recall, and format accuracy
5. Overall score computed as weighted combination

### Evaluation Metrics

**Overall Performance:**
- Overall Score: 72%
- Answer Quality: 83%
- Citation Accuracy: 70%
- Retrieval Quality: 59%

**By Question Type:**
- Specific Questions: 79%
- Comparative Questions: 77%
- Factual Questions: 73%
- Complex Questions: 69%
- Broad Questions: 60%

**By Difficulty:**
- Medium: 78%
- Easy: 73%
- Hard: 65%

### Test Results Files

All evaluation results are stored in `evaluation/results/`:

**Individual Test Results** (`evaluation/results/article_{id}/question_{n}.json`):
Each JSON file contains:
- Question text and metadata (type, difficulty)
- Retrieval scores (strict_recall_at_k, soft_recall_at_k)
- Answer scores (semantic_similarity, key_facts_coverage)
- Citation scores (precision, recall, accuracy)
- Overall score

**Aggregate Results** (`evaluation/results/aggregate_results.json`):
Summary statistics including:
- Overall system performance
- Performance by question type
- Performance by difficulty level
- Performance by article

**Analysis Documents:**
- `PRESENTATION_METRICS.md`: Formatted results for presentations
- `BEST_RAG_RESULTS.md`: Top 5 performing examples with details

### Running Evaluation

The evaluation system is included in the `evaluation/` directory and can be run to test the RAG system.

**Setup:**
```bash
cd evaluation

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Run Full Evaluation:**
```bash
# Run all 181 test cases (takes ~15-30 minutes)
python run_evaluation.py

# Run with cached RAG outputs (skip re-querying, just recalculate metrics)
python run_evaluation.py --use-cache

# Run specific article only
python run_evaluation.py --article 207
```

**What happens:**
1. Loads test cases from `data/test_set/`
2. Queries RAG system for each question (or uses cache)
3. Saves RAG outputs to `data/rag_outputs/`
4. Calculates retrieval, answer, and citation metrics
5. Saves individual results to `results/article_{id}/question_{n}.json`
6. Generates aggregate summary in `results/aggregate_results.json`

**Analyze Results:**
```bash
# Analyze pre-computed results
python find_best_questions.py
```

This script outputs:
- Top 20 questions by overall score
- Diverse set of 5 best examples across different question types
- Performance breakdown by type and difficulty

## Configuration

### Environment Variables

Backend `.env` file:

```bash
# Required
GEMINI_API_KEY=your-gemini-api-key-here
QDRANT_URL=https://your-cluster.cloud.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key-here

# Optional
MODEL_NAME=gemini-1.5-flash-latest
MAX_RESPONSE_TOKENS=2048
COLLECTION_NAME=nasa_corpus_v1
TOP_K=15
SERPAPI_API_KEY=your-serpapi-key  # For Google Scholar search and image search
```

### Settings File (`backend/settings.py`)

Configuration loaded from environment variables using Pydantic Settings:

```python
class Settings(BaseSettings):
    GEMINI_API_KEY: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    MODEL_NAME: str = "gemini-1.5-flash-latest"
    MAX_RESPONSE_TOKENS: int = 2048
    COLLECTION_NAME: str = "nasa_corpus_v1"
    TOP_K: int = 15
```

## Tech Stack

### Backend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | FastAPI 0.104 | Async HTTP API |
| Agent Framework | LangChain 0.2+ | ReAct agent orchestration |
| LLM | Google Gemini 1.5 Flash | Answer generation |
| Vector DB | Qdrant Cloud | Hybrid vector search |
| Embeddings | MiniLM-L6-v2 + Splade_PP | Dense + sparse vectors |
| Validation | Pydantic 2.7+ | Request/response models |
| Environment | python-dotenv | Config management |

### Frontend

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Framework | Next.js 15.5 | React meta-framework |
| UI Library | React 19 | Component library |
| Styling | TailwindCSS 3.4 | Utility-first CSS |
| Language | TypeScript 5 | Type safety |
| HTTP Client | Fetch API | Backend communication |

## Development

### Backend Development

**Run in development mode:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Run tests:**
```bash
pytest
```

**Test specific components:**
```bash
# Test RAG integration
python test_rag_integration.py

# Test agent reasoning
python test_agent_reasoning.py

# Test session endpoints
python test_session_endpoint.py
```

### Frontend Development

**Development server with hot reload:**
```bash
npm run dev
```

**Build for production:**
```bash
npm run build
npm start
```

**Type checking:**
```bash
npm run type-check
```

### Code Structure Guidelines

**Backend:**
- Use Pydantic models for all request/response types
- Handle errors gracefully with try/except and informative messages
- Log important events (session creation, RAG calls, errors)
- Follow FastAPI best practices for async/await

**Frontend:**
- Use TypeScript for all components
- Follow React hooks patterns
- Keep components focused and reusable
- Handle loading and error states explicitly

## Troubleshooting

### Common Issues

**1. Qdrant Connection Error**

```
Error: Could not connect to Qdrant
```

**Solution:** Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env` file. Check network connectivity to Qdrant Cloud.

**2. Gemini API Error**

```
Error: Invalid API key
```

**Solution:** Verify `GEMINI_API_KEY` is set correctly. Check API quota limits.

**3. Empty Retrieval Results**

```
Warning: No documents retrieved
```

**Solution:** Verify collection name matches. Check if collection has data. Try broader query terms.

**4. Frontend Cannot Connect to Backend**

```
Error: Failed to fetch
```

**Solution:** Ensure backend is running on `http://localhost:8000`. Check CORS settings in `main.py`.

**5. Session Not Persisting**

**Note:** Sessions use in-memory storage by default. Sessions will be lost on server restart. For persistence, integrate a database (see `session_manager.py`).

**6. No Data / Collection Empty**

```
Warning: No documents retrieved
```

**Solution:** Your Qdrant collection is empty or doesn't exist.
- Verify `COLLECTION_NAME` in `.env` matches your populated collection
- Check collection exists in Qdrant dashboard
- Ensure you've completed data setup (see Installation > Data Setup section)
- Test retrieval directly: `PYTHONPATH=$PWD python -m retrieval.query_cli --query "test" --collection your_collection_name`

### Debug Mode

Enable verbose logging:

```python
# In settings.py or main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

View agent reasoning:

```python
# In generation/agent_service.py
self.agent_executor = AgentExecutor(
    agent=self.agent,
    tools=[self.rag_tool],
    verbose=True,  # Set to True
    ...
)
```

## Contributing

### Adding New Papers to the Corpus

1. Process papers into chunks (Abstract, Methods, Results, Discussion)
2. Generate dense and sparse embeddings
3. Upload to Qdrant collection with metadata:
   ```python
   {
       "id": "PMC12345:results:uuid",
       "pmc_id": "PMC12345",
       "section": "results",
       "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12345/",
       "text": "chunk content...",
       "publication_date": "2024-01-15"
   }
   ```

### Extending the Agent

Add new tools in `generation/agent_service.py`:

```python
from langchain.tools import Tool

new_tool = Tool(
    name="tool_name",
    func=your_function,
    description="When to use this tool..."
)

# Add to agent creation
tools = [self.rag_tool, new_tool]
```

### Creating Custom Test Cases

Add new test cases in `evaluation/data/test_set/article_{id}_test_cases.json`:

```json
{
  "article_number": 123,
  "pmc_id": "PMC12345",
  "test_cases": [
    {
      "question": "Your test question?",
      "question_type": "factual|comparative|complex|specific|broad",
      "difficulty": "easy|medium|hard",
      "ground_truth": {
        "answer": "Expected answer text...",
        "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
        "must_retrieve_chunks": ["PMC12345:results:uuid1"],
        "should_retrieve_chunks": ["PMC12345:discussion:uuid2"],
        "expected_citations": ["PMC12345:results:uuid1"]
      }
    }
  ]
}
```

Then run evaluation:
```bash
cd evaluation
python run_evaluation.py --article 123
```

Results will be saved to `evaluation/results/article_123/`.

## License

This project is for educational and research purposes. NASA data is publicly available.

## Acknowledgments

- NASA Biological and Physical Sciences Division for the research corpus
- PubMed Central for open access publications
- Google for Gemini API access
- Qdrant for vector database infrastructure
