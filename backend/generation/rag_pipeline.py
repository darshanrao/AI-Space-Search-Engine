"""
RAG (Retrieval-Augmented Generation) pipeline that combines retrieval and generation.
"""
from __future__ import annotations

import click
from typing import Dict, Any, List
from .retrieval_client import RetrievalClient
from .gemini_client import GeminiClient


class RAGPipeline:
    """Main RAG pipeline that combines retrieval and generation."""
    
    def __init__(
        self, 
        collection_name: str = "nasa_corpus_v1",
        top_k: int = 10,  # Fixed to 15 chunks
        max_tokens: int = 1000
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            collection_name: Name of the Qdrant collection
            top_k: Number of documents to retrieve (ignored, always uses 15)
            max_tokens: Maximum tokens for generation
        """
        self.retrieval_client = RetrievalClient(collection_name)
        self.gemini_client = GeminiClient()
        self.top_k = 15  # Always use 15 chunks
        self.max_tokens = max_tokens
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a query through the complete RAG pipeline.
        
        Args:
            question: The user's question
            
        Returns:
            Dictionary containing the answer and metadata
        """
        try:
            # Step 1: Retrieve relevant documents
            retrieved_docs = self.retrieval_client.retrieve_top_k(question, self.top_k)
            
            if not retrieved_docs:
                return {
                    "answer": "I couldn't find any relevant information in the knowledge base to answer your question.",
                    "retrieved_docs": [],
                    "num_docs": 0,
                    "success": False
                }
            
            # Step 2: Pass full document metadata to Gemini for proper URL handling
            # Step 3: Generate answer using Gemini
            answer = self.gemini_client.generate_answer(question, retrieved_docs, self.max_tokens)
            
            # Step 4: Prepare response
            return {
                "answer": answer,
                "retrieved_docs": retrieved_docs,
                "num_docs": len(retrieved_docs),
                "success": True,
                "question": question
            }
            
        except Exception as e:
            return {
                "answer": f"An error occurred while processing your question: {str(e)}",
                "retrieved_docs": [],
                "num_docs": 0,
                "success": False,
                "error": str(e)
            }
    
    def get_retrieval_only(self, question: str) -> List[Dict[str, Any]]:
        """
        Get only the retrieval results without generation.
        
        Args:
            question: The user's question
            
        Returns:
            List of retrieved documents
        """
        return self.retrieval_client.retrieve_top_k(question, self.top_k)


@click.command()
@click.option("--question", required=True, type=str, help="The question to answer")
@click.option("--collection", default="nasa_corpus_v1", type=str, help="Qdrant collection name")
@click.option("--top-k", default=15, type=int, help="Number of documents to retrieve (always uses 15)")
@click.option("--max-tokens", default=1000, type=int, help="Maximum tokens for generation")
@click.option("--retrieval-only", is_flag=True, help="Only show retrieval results, don't generate answer")
def main(
    question: str, 
    collection: str, 
    top_k: int, 
    max_tokens: int,
    retrieval_only: bool
) -> None:
    """Run the RAG pipeline with the given question."""
    
    try:
        # Initialize pipeline (always uses 15 chunks)
        pipeline = RAGPipeline(collection, 15, max_tokens)
        
        if retrieval_only:
            # Show only retrieval results
            print(f"🔍 Retrieving top 15 documents for: '{question}'\n")
            docs = pipeline.get_retrieval_only(question)
            
            for i, doc in enumerate(docs, 1):
                print(f"[{i}] Score: {doc['score']:.4f} | Section: {doc['section']}")
                print(f"ID: {doc['id']}")
                print(f"Text: {doc['text'][:200]}...")
                print("-" * 80)
        
        else:
            # Run complete RAG pipeline
            print(f"🤖 Processing question: '{question}'\n")
            result = pipeline.query(question)
            
            if result["success"]:
                print("📚 Retrieved Documents:")
                for i, doc in enumerate(result["retrieved_docs"][:3], 1):  # Show top 3
                    print(f"  [{i}] {doc['section']} (score: {doc['score']:.4f})")
                
                print(f"\n✅ Answer (based on {result['num_docs']} documents):")
                print("=" * 80)
                print(result["answer"])
                print("=" * 80)
            else:
                print("❌ Failed to generate answer:")
                print(result["answer"])
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
