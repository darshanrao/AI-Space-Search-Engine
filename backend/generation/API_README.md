# RAG API Module

This module provides clean API functions for the RAG generation system, designed for easy integration and debugging.

## Functions

### `query_rag_json(question, collection_name="nasa_corpus_v1")`

Returns clean JSON output for integration with other systems.

**Parameters:**
- `question` (str): The research question to answer
- `collection_name` (str): Qdrant collection name (default: "nasa_corpus_v1")

**Returns:**
```python
{
    "answer_markdown": "Generated answer with inline citations [1], [2]...",
    "citations": [
        {
            "id": "PMC10751425:discussion:7b0f4426",
            "url": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10751425/",
            "why_relevant": "Brief explanation of relevance"
        }
    ],
    "image_citations": [],
    "used_context_ids": ["chunk-id-1", "chunk-id-2", ...],
    "confident": true
}
```

**Usage:**
```python
from generation.api import query_rag_json

result = query_rag_json("Which genes are implicated in bisphosphonate-mediated muscle improvements?")
print(result["answer_markdown"])
```

### `query_rag_debug(question, output_file=None, collection_name="nasa_corpus_v1")`

Generates detailed debug output saved to a text file for development and debugging.

**Parameters:**
- `question` (str): The research question to answer
- `output_file` (str, optional): Output file path. If None, auto-generates filename.
- `collection_name` (str): Qdrant collection name (default: "nasa_corpus_v1")

**Returns:**
- `str`: Path to the generated debug file

**Debug File Contents:**
- Question and timestamp
- All 15 retrieved chunks with:
  - Citation ID (from chunk metadata)
  - Document ID
  - Relevance score
  - Section information
  - URL
  - Full content
- Complete generated answer in JSON format

**Usage:**
```python
from generation.api import query_rag_debug

debug_file = query_rag_debug("How do astronauts grow food in space?")
print(f"Debug info saved to: {debug_file}")
```

## Features

✅ **15 Chunks Always**: System always retrieves 15 chunks for comprehensive analysis  
✅ **Proper Citation IDs**: Uses "id" field from chunk metadata, not document IDs  
✅ **Clean JSON**: Structured output ready for integration  
✅ **Debug Output**: Complete transparency with all retrieved content  
✅ **Error Handling**: Graceful handling of API failures  
✅ **No Token Limits**: Full responses without artificial truncation  

## Integration Example

```python
from generation.api import query_rag_json

def research_question(question):
    """Simple wrapper for research queries."""
    result = query_rag_json(question)
    
    if result["confident"]:
        return {
            "success": True,
            "answer": result["answer_markdown"],
            "sources": len(result["citations"]),
            "citations": result["citations"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error", "Unknown error"),
            "answer": result["answer_markdown"]
        }

# Usage
response = research_question("What are the effects of microgravity on bone density?")
if response["success"]:
    print(f"Answer: {response['answer']}")
    print(f"Based on {response['sources']} sources")
else:
    print(f"Error: {response['error']}")
```

## Requirements

- Gemini API key set in environment variables (`GEMINI_API_KEY`)
- Qdrant credentials in `.env` file
- All dependencies installed (`pip install -r requirements.txt`)

## Error Handling

Both functions include comprehensive error handling:
- Missing API keys
- Network connectivity issues
- JSON parsing failures
- Empty retrieval results
- Gemini API failures

Errors are returned in a structured format with appropriate error messages.
