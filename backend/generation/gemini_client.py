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
2) Each citation number must correspond to the ORDER in the "citations" URL array (first URL = [1], second URL = [2], etc.).
3) Use separate brackets for each citation: [1], [2], [3] NOT [1,2,3].
4) If you used any chunks of kind "caption" (e.g., charts, screenshots, figures) to support the answer, extract JPG URLs from the chunk text content (URLs ending with .jpg) and include them in "image_citations".
5) For regular citations, NEVER invent sources or URLs. Use ONLY the URLs from the "URL" field in the context.
6) DO NOT extract URLs from the content text for regular citations (like DOIs, PubMed links, etc.).
7) If a chunk has no "URL" field, use "N/A" as the URL value.
8) Don't cite on duplicate links - citations should be linkwise not chunkwise, so don't use [1], [2], [3], [4] for the same link.
9) Only include URLs that were actually used to support your answer.
10) Write a comprehensive and detailed answer to the question. Provide thorough explanations, context, and supporting evidence.
11) Use double line breaks (\\n\\n) between paragraphs to create clear, readable sections. Each major topic or concept should be in its own paragraph.
12) No hidden reasoning or chain-of-thought in the output. Produce ONLY the required fields.
13) Provide a confidence score from 0-100 based on how confident you are in the answer quality.
14) Include relevant keywords that could be used to search for related images (e.g., scientific concepts, organisms, equipment, processes mentioned in your answer).

 Output format (JSON):
 {{
   "answer_markdown": "Comprehensive answer with proper paragraph spacing using \\n\\n between sections. Include detailed explanations with inline [1], [2], [3] citations.",
   "citations": [
     "https://example.com/paper1",
     "https://example.com/paper2"
   ],
   "image_citations": [
     {{"id":"ctx-id", "url":"https://...", "caption_or_alt":"short description"}}
   ],
   "image_keywords": [
     "C. elegans muscle",
     "microgravity effects",
     "space biology"
   ],
   "confidence_score": 85
 }}

Validation:
- Every [n] in answer_markdown must have a matching URL in "citations" array at position n-1.
- URLs must come from CONTEXT exactly (no rewriting).
- Citations array should contain only unique URLs in the order they first appear in your answer.
- Each unique URL gets only ONE citation number, regardless of how many chunks from that URL you use.
- Image citations should only include JPG URLs from chunks that were actually used to support the answer.
- Output MUST be valid JSON only - no additional text outside the JSON structure.
- Do not include any text after the JSON closing brace."""
        
        return prompt
