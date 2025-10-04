"""
Gemini API client for generating answers from retrieved context.
"""
from __future__ import annotations

import os
from typing import List, Optional
import google.generativeai as genai
from dotenv import load_dotenv


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize the Gemini client."""
        # Load API key from environment
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY must be set in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_answer(
        self, 
        query: str, 
        retrieved_docs: List[Dict[str, Any]], 
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate an answer using Gemini based on the query and context.
        
        Args:
            query: The user's question
            retrieved_docs: List of retrieved documents with metadata
            max_tokens: Maximum tokens for the response
            
        Returns:
            Generated answer string
        """
        try:
            # Create the prompt
            prompt = self._create_prompt(query, retrieved_docs)
            
            # Generate response
            generation_config = {}
            if max_tokens:
                generation_config['max_output_tokens'] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {str(e)}")
    
    def _create_prompt(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Create a well-structured prompt for the Gemini model.
        
        Args:
            query: The user's question
            retrieved_docs: List of retrieved documents with metadata
            
        Returns:
            Formatted prompt string
        """
        # Combine context chunks with metadata including URL information
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            # Extract URL from metadata if available
            url = doc.get('full_payload', {}).get('url', 'N/A')
            # Extract citation ID from metadata if available
            citation_id = doc.get('full_payload', {}).get('id', f"ctx-{i+1}")
            
            # Format context with URL information
            context_parts.append(f"Context {i+1}:\nCitation ID: {citation_id}\nText: {doc['text']}\nURL: {url}\nSection: {doc['section']}\nDocument ID: {doc['id']}")
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""You are a RAG answerer. Your job is to answer the user's question ONLY using the provided CONTEXT.
If the context is insufficient, say so clearly and suggest what information is missing.

CONTEXT INFORMATION:
{context}

QUESTION: {query}

Rules:
1) Cite every non-trivial claim with inline numeric citations like [1], [2], [3].
2) Each citation number must correspond to the ORDER in the "citations" array (first citation = [1], second = [2], etc.).
3) Use separate brackets for each citation: [1], [2], [3] NOT [1,2,3].
4) If you used any chunks of kind "caption" (e.g., charts, screenshots, figures) to support the answer,
   mention them inline as [img 1], [img 2] AND include their JPG URLs in "image_citations".
5) For image citations, extract JPG URLs from the chunk text content (URLs ending with .jpg).
6) For regular citations, NEVER invent sources or URLs. Use ONLY the URLs from the "URL" field in the context.
7) DO NOT extract URLs from the content text for regular citations (like DOIs, PubMed links, etc.).
8) If a chunk has no "URL" field, use "N/A" as the URL value.
9) Use ONLY the "Citation ID" field for the citation ID, NOT the Document ID.
10) DO NOT include titles in citations - only use the "why_relevant" field.
11) Prefer concise, direct answers; add a brief "Why this is correct" note if helpful.
12) No hidden reasoning or chain-of-thought in the output. Produce ONLY the required fields.

Output format (JSON):
{{
  "answer_markdown": "string with inline [1], [2], and [img 1] citations",
  "citations": [
    {{"id":"citation-id", "url":"https://...", "why_relevant":"one short phrase"}}
  ],
  "image_citations": [
    {{"id":"ctx-id", "url":"https://...", "caption_or_alt":"short description"}}
  ],
  "used_context_ids": ["ctx-id-1", "ctx-id-2", ...],
  "confident": true
}}

Validation:
- Every [n] in answer_markdown must have a matching entry in "citations" (order should align).
- Every [img n] must have a matching entry in "image_citations" (order should align).
- URLs must come from CONTEXT exactly (no rewriting).
- Output MUST be valid JSON only - no additional text outside the JSON structure.
- Do not include any text after the JSON closing brace."""
        
        return prompt
