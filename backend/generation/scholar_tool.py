"""
Google Scholar Search Tool using SerpApi.
Provides academic paper search functionality for the RAG system.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from serpapi import GoogleSearch
from settings import settings
from .query_generator import query_generator


class ScholarSearchInput(BaseModel):
    """Input schema for Google Scholar search."""
    query: str = Field(description="The academic research query to search for in Google Scholar")
    num_results: int = Field(default=5, description="Number of results to return (default: 5, max: 20)")


class ScholarSearchTool(BaseTool):
    """Tool for searching Google Scholar using SerpApi."""
    
    name: str = "google_scholar_search"
    description: str = (
        "Search Google Scholar for academic papers and research articles. "
        "Use this when you need to find recent academic publications, research papers, "
        "or scholarly articles related to a specific topic. "
        "Input should be a clear research question or topic keywords."
    )
    args_schema: type[BaseModel] = ScholarSearchInput
    api_key: Optional[str] = None
    
    def __init__(self):
        super().__init__()
        self.api_key = getattr(settings, 'SERPAPI_API_KEY', None)
        if not self.api_key:
            print("Warning: SERPAPI_API_KEY not found in settings. Google Scholar search will be disabled.")
    
    def _run(self, query: str, num_results: int = 5) -> str:
        """
        Execute Google Scholar search.
        
        Args:
            query: The search query
            num_results: Number of results to return (default: 5, max: 20)
            
        Returns:
            Formatted string with search results
        """
        if not self.api_key:
            return "Google Scholar search is not available. SERPAPI_API_KEY is not configured."
        
        if not query.strip():
            return "Please provide a valid search query."
        
        # Limit results to reasonable number
        num_results = min(max(num_results, 1), 20)
        
        try:
            # Search parameters for Google Scholar
            params = {
                "q": query,
                "engine": "google_scholar",
                "api_key": self.api_key,
                "num": num_results,
                "hl": "en",  # Language
                "gl": "us"   # Country
            }
            
            # Perform the search
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Parse and format results
            return self._format_results(results, query)
            
        except Exception as e:
            return f"Error searching Google Scholar: {str(e)}"
    
    def _format_results(self, results: Dict[str, Any], query: str) -> str:
        """
        Format Google Scholar search results into a readable string.
        
        Args:
            results: Raw search results from SerpApi
            query: Original search query
            
        Returns:
            Formatted string with search results
        """
        if "organic_results" not in results or not results["organic_results"]:
            return f"No academic papers found for query: '{query}'"
        
        formatted_results = []
        formatted_results.append(f"🔍 Google Scholar Results for: '{query}'")
        formatted_results.append("=" * 80)
        formatted_results.append("")
        
        for i, result in enumerate(results["organic_results"], 1):
            # Extract basic information
            title = result.get("title", "No title")
            link = result.get("link", "")
            snippet = result.get("snippet", "No abstract available")
            
            # Extract publication information
            publication_info = result.get("publication_info", {})
            authors = publication_info.get("summary", "Authors not specified")
            
            # Extract citation information
            inline_links = result.get("inline_links", {})
            cited_by = inline_links.get("cited_by", {})
            citation_count = cited_by.get("total", 0) if cited_by else 0
            
            # Format the result with cleaner structure
            formatted_results.append(f"📄 Paper #{i}")
            formatted_results.append("─" * 60)
            formatted_results.append(f"📌 Title: {title}")
            formatted_results.append("")
            formatted_results.append(f"👥 Authors: {authors}")
            if citation_count > 0:
                formatted_results.append(f"📊 Citations: {citation_count}")
            formatted_results.append(f"🔗 Link: {link}")
            formatted_results.append("")
            formatted_results.append(f"📝 Abstract: {snippet[:300]}{'...' if len(snippet) > 300 else ''}")
            formatted_results.append("")
            formatted_results.append("")  # Extra spacing between papers
        
        # Add related searches if available
        if "related_searches" in results and results["related_searches"]:
            formatted_results.append("🔍 Related Search Suggestions:")
            formatted_results.append("─" * 60)
            for related in results["related_searches"][:3]:  # Show top 3 related searches
                formatted_results.append(f"• {related.get('query', '')}")
            formatted_results.append("")
        
        return "\n".join(formatted_results)
    
    async def _arun(self, query: str, num_results: int = 5) -> str:
        """Async version of the search tool."""
        return self._run(query, num_results)
    
    def search_with_context(self, conversation_context: str, user_query: Optional[str] = None, num_results: int = 5) -> tuple[str, str]:
        """
        Search Google Scholar using LLM-generated query from conversation context.
        
        Args:
            conversation_context: Recent conversation messages
            user_query: Optional explicit user query
            num_results: Number of results to return
            
        Returns:
            Tuple of (generated_query, formatted_results)
        """
        try:
            # Generate optimized query using LLM
            optimized_query = query_generator.generate_scholar_query(conversation_context, user_query)
            
            print(f"Generated Google Scholar query: '{optimized_query}'")
            
            # Perform search with optimized query
            results = self._run(optimized_query, num_results)
            return optimized_query, results
            
        except Exception as e:
            print(f"Error in context-based search: {e}")
            # Fallback to simple search
            fallback_query = user_query or "space biology research"
            results = self._run(fallback_query, num_results)
            return fallback_query, results


# Global scholar search tool instance
scholar_search_tool = ScholarSearchTool()
