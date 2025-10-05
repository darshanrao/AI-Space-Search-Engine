"""
RAG Tool for LangChain Agent.
This tool allows the agent to decide when to use RAG for information retrieval.
"""

from typing import Type, Dict, Any, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .api import query_rag_json


class RAGSearchInput(BaseModel):
    """Input for the RAG search tool."""
    query: str = Field(description="The scientific question to search for in the space biology corpus")


class RAGSearchTool(BaseTool):
    """Tool for searching the space biology corpus using RAG."""
    
    name: str = "search_space_biology_corpus"
    description: str = (
        "Search a curated database of 608 Space Biology publications from PubMed Central (2010-present). "
        "ONLY use this tool when you need specific research findings, experimental data, or citations from published space biology studies. "
        "This database contains peer-reviewed research papers on space biology topics like microgravity effects, space radiation, "
        "biological experiments in space, and related scientific studies. Do NOT use for general scientific concepts or basic definitions."
    )
    args_schema: Type[BaseModel] = RAGSearchInput
    
    def _run(self, query: str) -> str:
        """Execute the RAG search."""
        try:
            # Use the existing RAG pipeline
            result = query_rag_json(query)
            
            if result.get("error"):
                return f"Error searching corpus: {result['error']}"
            
            # Format the response for the agent
            answer = result.get("answer_markdown", "")
            citations = result.get("citations", [])
            confidence = result.get("confidence_score", 0)
            
            # Create a concise structured response
            response = f"{answer}\n\n"
            
            if citations:
                response += f"Sources: {', '.join([f'[{i+1}]' for i in range(len(citations))])}\n"
                response += f"URLs: {'; '.join(citations[:3])}"  # Show first 3 URLs only
                if len(citations) > 3:
                    response += f" (and {len(citations)-3} more)"
            else:
                response += "No sources found."
            
            return response
            
        except Exception as e:
            return f"Error during RAG search: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        """Async version of the RAG search."""
        return self._run(query)
