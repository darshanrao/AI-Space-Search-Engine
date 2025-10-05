"""
API functions for the RAG generation system.
Provides clean JSON output for integration and debug file output for development.
"""
from __future__ import annotations

import json
from typing import Dict, Any, Optional
from .rag_pipeline import RAGPipeline


class RAGAPI:
    """API class for RAG generation with clean JSON and debug output."""
    
    def __init__(self, collection_name: str = "nasa_corpus_v1"):
        """Initialize the RAG API."""
        self.pipeline = RAGPipeline(collection_name, top_k=15, max_tokens=None)
    
    def query_json(self, question: str) -> Dict[str, Any]:
        """
        Generate an answer and return clean JSON for integration.
        
        Args:
            question: The user's question
            
        Returns:
            Dictionary with the generated answer and metadata
        """
        try:
            result = self.pipeline.query(question)
            
            if not result["success"]:
                return {
                    "answer_markdown": result["answer"],
                    "citations": [],
                    "image_citations": [],
                    "confidence_score": 0,
                    "error": result.get("error", "Unknown error")
                }
            
            # Parse the JSON response from Gemini
            try:
                # Clean the response - remove markdown code blocks if present
                answer_text = result["answer"]
                if "```json" in answer_text:
                    # Extract JSON from markdown code block
                    start = answer_text.find("```json") + 7
                    end = answer_text.find("```", start)
                    if end != -1:
                        answer_text = answer_text[start:end].strip()
                elif "```" in answer_text:
                    # Extract JSON from generic code block
                    start = answer_text.find("```") + 3
                    end = answer_text.find("```", start)
                    if end != -1:
                        answer_text = answer_text[start:end].strip()
                else:
                    # No markdown blocks - try to find JSON by looking for first { and last }
                    first_brace = answer_text.find('{')
                    last_brace = answer_text.rfind('}')
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        answer_text = answer_text[first_brace:last_brace + 1]
                
                # Additional cleanup - find the first { and last } to ensure clean JSON
                if not answer_text.strip().startswith('{'):
                    first_brace = answer_text.find('{')
                    if first_brace != -1:
                        answer_text = answer_text[first_brace:]
                
                if not answer_text.strip().endswith('}'):
                    last_brace = answer_text.rfind('}')
                    if last_brace != -1:
                        answer_text = answer_text[:last_brace + 1]
                
                json_response = json.loads(answer_text)
                
                # Manual double-check: ensure citations are unique URLs only
                if "citations" in json_response:
                    citations = json_response["citations"]
                    if isinstance(citations, list):
                        # Remove duplicates while preserving order
                        unique_citations = []
                        seen_urls = set()
                        for citation in citations:
                            if isinstance(citation, str) and citation not in seen_urls:
                                unique_citations.append(citation)
                                seen_urls.add(citation)
                            elif isinstance(citation, dict) and "url" in citation:
                                # Handle old format as fallback
                                url = citation["url"]
                                if url not in seen_urls:
                                    unique_citations.append(url)
                                    seen_urls.add(url)
                        json_response["citations"] = unique_citations
                
                # Search for images using keywords if available
                if "image_keywords" in json_response and json_response["image_keywords"]:
                    from image_search_service import image_search_service
                    image_urls = image_search_service.search_images_for_keywords(json_response["image_keywords"])
                    json_response["image_urls"] = image_urls
                else:
                    json_response["image_urls"] = []
                
                return json_response
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                return {
                    "answer_markdown": result["answer"],
                    "citations": [],
                    "image_citations": [],
                    "confidence_score": 0,
                    "error": f"Failed to parse JSON response: {str(e)}"
                }
                
        except Exception as e:
            return {
                "answer_markdown": f"An error occurred: {str(e)}",
                "citations": [],
                "image_citations": [],
                "confidence_score": 0,
                "error": str(e)
            }
    
    def query_debug_file(
        self, 
        question: str, 
        output_file: str = None
    ) -> str:
        """
        Generate an answer and save detailed debug output to a text file.
        
        Args:
            question: The user's question
            output_file: Optional output file path. If None, auto-generates filename.
            
        Returns:
            Path to the generated debug file
        """
        import os
        from datetime import datetime
        
        # Generate filename if not provided
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_question = "".join(c for c in question[:50] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_file = f"debug_rag_{timestamp}_{safe_question.replace(' ', '_')}.txt"
        
        try:
            # Get retrieval results
            retrieved_docs = self.pipeline.get_retrieval_only(question)
            
            # Generate answer
            result = self.pipeline.query(question)
            
            # Prepare debug output
            output_lines = []
            output_lines.append(f"🤖 DEBUG OUTPUT - RAG Generation")
            output_lines.append(f"Timestamp: {datetime.now().isoformat()}")
            output_lines.append(f"Question: '{question}'")
            output_lines.append("=" * 100 + "\n")
            
            # Add retrieval information
            output_lines.append(f"📚 RETRIEVED DOCUMENTS ({len(retrieved_docs)} total):")
            output_lines.append("=" * 100 + "\n")
            
            for i, doc in enumerate(retrieved_docs, 1):
                # Use the "id" field from chunk metadata for citation ID
                citation_id = doc.get('full_payload', {}).get('id', f'chunk-{i}')
                url = doc.get('full_payload', {}).get('url', 'N/A')
                
                output_lines.append(f"[CHUNK {i}]")
                output_lines.append(f"Citation ID: {citation_id}")
                output_lines.append(f"Document ID: {doc['id']}")
                output_lines.append(f"Score: {doc['score']:.4f}")
                output_lines.append(f"Section: {doc['section']}")
                output_lines.append(f"URL: {url}")
                output_lines.append(f"Content:")
                output_lines.append(f"{doc['text']}")
                output_lines.append("-" * 100 + "\n")
            
            # Add generation result
            if result["success"]:
                output_lines.append(f"\n✅ GENERATED ANSWER:")
                output_lines.append("=" * 100 + "\n")
                output_lines.append(result["answer"])
                output_lines.append("=" * 100 + "\n")
            else:
                output_lines.append(f"\n❌ GENERATION FAILED:")
                output_lines.append("=" * 100 + "\n")
                output_lines.append(result["answer"])
                output_lines.append("=" * 100 + "\n")
            
            # Save to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(output_lines))
            
            print(f"💾 Debug output saved to: {output_file}")
            return output_file
            
        except Exception as e:
            error_msg = f"❌ Error generating debug file: {str(e)}"
            print(error_msg)
            
            # Save error to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Error: {str(e)}")
            
            return output_file


# Convenience functions for easy import
def query_rag_json(question: str, collection_name: str = "nasa_corpus_v1") -> Dict[str, Any]:
    """
    Simple function to query RAG and return JSON.
    
    Args:
        question: The user's question
        collection_name: Qdrant collection name
        
    Returns:
        Dictionary with the generated answer and metadata
    """
    api = RAGAPI(collection_name)
    return api.query_json(question)


def query_rag_debug(question: str, output_file: str = None, collection_name: str = "nasa_corpus_v1") -> str:
    """
    Simple function to query RAG and save debug output to file.
    
    Args:
        question: The user's question
        output_file: Optional output file path
        collection_name: Qdrant collection name
        
    Returns:
        Path to the generated debug file
    """
    api = RAGAPI(collection_name)
    return api.query_debug_file(question, output_file)
