# Generation Pipeline

This module implements a RAG (Retrieval-Augmented Generation) pipeline that combines the retrieval system with Google Gemini for answer generation.

## Features

- **Hybrid Retrieval**: Uses the existing retrieval system to find top-k relevant documents
- **Gemini Integration**: Leverages Google Gemini API for high-quality answer generation
- **Context-Aware**: Provides retrieved documents as context to the LLM
- **Configurable**: Supports different collections, top-k values, and token limits

## Setup

### 1. Environment Variables

Add your Gemini API key to the `.env` file in the repo root:

```bash
# Add to .env file
GEMINI_API_KEY=your-gemini-api-key-here
```

### 2. Dependencies

The required dependencies are already installed:
- `google-generativeai` - For Gemini API integration
- `python-dotenv` - For environment variable management

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Generate an answer for a question
PYTHONPATH=$PWD python -m generation.cli \
  --question "What are microgravity effects on stem cells?" \
  --top-k 10 \
  --max-tokens 1000
```

#### Advanced Usage
```bash
# Use different collection and parameters
PYTHONPATH=$PWD python -m generation.cli \
  --question "How do astronauts grow food in space?" \
  --collection nasa_corpus_v1 \
  --top-k 5 \
  --max-tokens 1500
```

### Using the RAG Pipeline Directly

```python
from generation.rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(
    collection_name="nasa_corpus_v1",
    top_k=10,
    max_tokens=1000
)

# Query the pipeline
result = pipeline.query("What are microgravity effects on stem cells?")

if result["success"]:
    print("Answer:", result["answer"])
    print("Documents used:", result["num_docs"])
else:
    print("Error:", result["answer"])
```

### Retrieval Only (No Generation)

```python
# Get only retrieval results without generating an answer
docs = pipeline.get_retrieval_only("What are microgravity effects on stem cells?")
for doc in docs:
    print(f"Score: {doc['score']}, Section: {doc['section']}")
```

## Architecture

```
User Query
    ↓
RAG Pipeline
    ↓
Retrieval Client → Qdrant → Top-k Documents
    ↓
Gemini Client → Context + Query → Generated Answer
    ↓
Response (Answer + Metadata)
```

## Components

### 1. `retrieval_client.py`
- Integrates with the existing retrieval system
- Handles Qdrant connection and hybrid search
- Returns formatted document results

### 2. `gemini_client.py`
- Manages Gemini API integration
- Creates structured prompts with context
- Handles API errors and rate limiting

### 3. `rag_pipeline.py`
- Main pipeline that orchestrates retrieval and generation
- Provides both retrieval-only and full RAG functionality
- Returns structured responses with metadata

### 4. `cli.py`
- Simple command-line interface
- Easy testing and demonstration

## Response Format

```python
{
    "answer": "Generated answer text",
    "retrieved_docs": [
        {
            "id": "document-id",
            "score": 0.5000,
            "text": "document text...",
            "section": "document section",
            "full_payload": {...}
        }
    ],
    "num_docs": 10,
    "success": True,
    "question": "original question"
}
```

## Error Handling

The pipeline includes comprehensive error handling:
- Missing API keys
- Network connectivity issues
- Empty retrieval results
- Gemini API failures

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for Gemini API access
- `QDRANT_URL`: Qdrant Cloud URL (inherited from retrieval system)
- `QDRANT_API_KEY`: Qdrant API key (inherited from retrieval system)

### Pipeline Parameters
- `collection_name`: Qdrant collection to search (default: "nasa_corpus_v1")
- `top_k`: Number of documents to retrieve (default: 10)
- `max_tokens`: Maximum tokens for Gemini generation (default: 1000)

## Example Output

```
🤖 Processing question: 'What are microgravity effects on stem cells?'

📚 Retrieved Documents:
  [1] Types of stem cells studied in space (score: 0.5000)
  [2] Microgravity-induced Stem Cell Alterations (score: 0.5000)
  [3] Current limitations and gaps (score: 0.3333)

✅ Answer (based on 10 documents):
================================================================================
Based on the research findings, microgravity has significant effects on stem cells:

1. **Cell Morphology Changes**: Microgravity causes alterations in cell shape and cytoskeletal organization in various types of stem cells.

2. **Gene Expression**: Studies show that microgravity affects gene expression profiles in stem cells, potentially impacting their differentiation capabilities.

3. **Proliferation Effects**: Some research indicates that microgravity may enhance cell proliferation in certain stem cell types, including mesenchymal stem cells.

4. **Differentiation Impact**: The regenerative potential of stem cells appears to be affected by microgravity conditions, with both positive and negative effects reported depending on the cell type.

The research suggests that microgravity creates a unique environment that fundamentally changes how stem cells behave, which has important implications for space medicine and potential therapeutic applications.
================================================================================
```
