"""
Retrieval client for integrating with the existing retrieval system.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models


class RetrievalClient:
    """Client for retrieving relevant documents from Qdrant."""
    
    def __init__(self, collection_name: str = "nasa_corpus_v1"):
        """Initialize the retrieval client."""
        # Load .env from repo root
        root = Path(__file__).resolve().parents[1]
        load_dotenv(dotenv_path=root / ".env", override=True)
        
        url = os.environ.get("QDRANT_URL")
        api_key = os.environ.get("QDRANT_API_KEY")
        
        if not url or not api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in .env file")
        
        self.client = QdrantClient(url=url, api_key=api_key, timeout=90.0)
        self.collection_name = collection_name
    
    def retrieve_top_k(
        self, 
        query: str, 
        k: int = 10,
        dense_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        sparse_model: str = "prithivida/Splade_PP_en_v1"
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k relevant documents using hybrid search.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            dense_model: Dense embedding model
            sparse_model: Sparse embedding model
            
        Returns:
            List of dictionaries containing document information
        """
        try:
            # Hybrid query with RRF using built-in Document wrappers
            resp = self.client.query_points(
                collection_name=self.collection_name,
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                prefetch=[
                    models.Prefetch(
                        query=models.Document(text=query, model=dense_model),
                        using="dense",
                    ),
                    models.Prefetch(
                        query=models.Document(text=query, model=sparse_model),
                        using="sparse",
                    ),
                ],
                limit=k,
                with_payload=True,
            )
            
            # Format results
            results = []
            for point in resp.points:
                payload = point.payload or {}
                text = (payload.get("text") or "").split("\n", 2)[-1]
                
                results.append({
                    "id": point.id,
                    "score": point.score,
                    "text": text,
                    "section": payload.get("section", "Unknown"),
                    "full_payload": payload
                })
            
            return results
            
        except Exception as e:
            raise RuntimeError(f"Retrieval failed: {str(e)}")
    
    def get_context_chunks(self, query: str, k: int = 10) -> List[str]:
        """
        Get just the text chunks for context.
        
        Args:
            query: The search query
            k: Number of chunks to retrieve
            
        Returns:
            List of text chunks
        """
        results = self.retrieve_top_k(query, k)
        return [result["text"] for result in results]
