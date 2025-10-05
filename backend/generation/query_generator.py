"""
Query Generator Service for Google Scholar Search.
Uses LLM to generate focused, academic search queries from conversation context.
"""

from typing import List, Optional
from generation.gemini_client import GeminiClient
import json
import re


class QueryGenerator:
    """Generates focused Google Scholar queries from conversation context."""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    def generate_scholar_query(self, conversation_context: str, user_query: Optional[str] = None) -> str:
        """
        Generate a focused Google Scholar search query from conversation context.
        
        Args:
            conversation_context: Recent conversation messages
            user_query: Optional explicit user query
            
        Returns:
            Optimized search query for Google Scholar
        """
        
        # If user provided explicit query, use it as base
        base_query = user_query.strip() if user_query and user_query.strip() else ""
        
        # Create prompt for query generation
        prompt = f"""You are an expert research assistant specializing in academic search optimization. 
Your task is to generate a focused, effective Google Scholar search query based on conversation context.

CONVERSATION CONTEXT:
{conversation_context}

{'USER QUERY: ' + base_query if base_query else 'NO EXPLICIT USER QUERY PROVIDED'}

INSTRUCTIONS:
1. Analyze the conversation context to identify the main research topic and key concepts
2. Extract relevant academic terms, scientific concepts, and research areas
3. Generate a focused Google Scholar search query that would find the most relevant academic papers
4. Use academic terminology and proper scientific keywords
5. Keep the query concise but comprehensive (2-8 key terms)
6. Prioritize terms that would appear in academic paper titles and abstracts
7. Include relevant scientific fields (e.g., "space biology", "microgravity", "C. elegans")
8. Consider synonyms and related terms that researchers might use

GOOGLE SCHOLAR QUERY GUIDELINES:
- Use academic terminology
- Include specific model organisms if mentioned (e.g., "C. elegans", "mice", "rats")
- Add experimental conditions (e.g., "microgravity", "spaceflight", "simulated microgravity")
- Include biological processes (e.g., "muscle development", "bone density", "gene expression")
- Add measurement techniques if relevant (e.g., "gene expression", "protein synthesis")
- Use Boolean operators if needed (AND, OR, NOT)

EXAMPLES OF GOOD QUERIES:
- "space biology microgravity muscle development C. elegans"
- "bone mineral density spaceflight hindlimb unloading mice"
- "gene expression microgravity effects space biology"
- "simulated microgravity effects on muscle atrophy"
- "spaceflight-induced changes in bone metabolism"

Generate ONLY the search query, nothing else. Do not include explanations or additional text."""

        try:
            # Generate query using Gemini
            response = self.gemini_client.generate_query(prompt)
            
            # Clean and validate the response
            query = self._clean_query(response)
            
            # Validate query length and content
            if not query or len(query) < 3:
                # Fallback to simple context extraction
                query = self._extract_fallback_query(conversation_context, base_query)
            
            return query
            
        except Exception as e:
            print(f"Error generating query with LLM: {e}")
            # Fallback to simple extraction
            return self._extract_fallback_query(conversation_context, base_query)
    
    def _clean_query(self, response: str) -> str:
        """Clean and validate the LLM-generated query."""
        # Remove any markdown formatting
        query = re.sub(r'[*_`]', '', response)
        
        # Remove quotes if present
        query = re.sub(r'^["\']|["\']$', '', query.strip())
        
        # Remove any prefix text like "Query:" or "Search:"
        query = re.sub(r'^(Query|Search|Scholar Query):\s*', '', query, flags=re.IGNORECASE)
        
        # Remove any suffix explanations
        query = query.split('\n')[0].strip()
        
        # Remove any trailing punctuation that's not part of the query
        query = re.sub(r'[.!?]+$', '', query)
        
        return query.strip()
    
    def _extract_fallback_query(self, conversation_context: str, user_query: Optional[str] = None) -> str:
        """Fallback method to extract key terms when LLM fails."""
        
        # Use user query if available
        if user_query and user_query.strip():
            return user_query.strip()
        
        # Extract key terms from conversation
        context_lower = conversation_context.lower()
        
        # Common space biology terms to look for
        key_terms = []
        
        # Scientific fields
        if any(term in context_lower for term in ['space biology', 'spaceflight', 'microgravity']):
            key_terms.append('space biology')
        
        # Model organisms
        organisms = ['c. elegans', 'caenorhabditis elegans', 'mice', 'rats', 'drosophila', 'zebrafish']
        for org in organisms:
            if org in context_lower:
                key_terms.append(org)
                break
        
        # Biological processes
        processes = ['muscle development', 'bone density', 'gene expression', 'protein synthesis', 
                    'muscle atrophy', 'bone loss', 'metabolism', 'development']
        for process in processes:
            if process in context_lower:
                key_terms.append(process)
                break
        
        # Experimental conditions
        conditions = ['microgravity', 'simulated microgravity', 'spaceflight', 'hindlimb unloading']
        for condition in conditions:
            if condition in context_lower:
                key_terms.append(condition)
                break
        
        # If no specific terms found, use general space biology terms
        if not key_terms:
            key_terms = ['space biology', 'microgravity', 'research']
        
        # Limit to 4 terms for better search results
        return ' '.join(key_terms[:4])


# Create global instance
query_generator = QueryGenerator()
