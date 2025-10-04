"""
Simple CLI for the RAG generation pipeline.
"""
from __future__ import annotations

import click
from .rag_pipeline import RAGPipeline


@click.command()
@click.option("--question", required=True, type=str, help="The question to answer")
@click.option("--collection", default="nasa_corpus_v1", type=str, help="Qdrant collection name")
@click.option("--top-k", default=15, type=int, help="Number of documents to retrieve (always uses 15)")
@click.option("--max-tokens", default=None, type=int, help="Maximum tokens for generation (None = no limit)")
@click.option("--output-file", default=None, type=str, help="Save output to file (e.g., output.txt)")
def generate_answer(question: str, collection: str, top_k: int, max_tokens: int, output_file: str) -> None:
    """Generate an answer using the RAG pipeline."""
    
    try:
        # Initialize pipeline (always uses 15 chunks)
        pipeline = RAGPipeline(collection, 15, max_tokens)
        
        # Run pipeline
        output_lines = []
        output_lines.append(f"🤖 Processing question: '{question}'\n")
        print(f"🤖 Processing question: '{question}'\n")
        
        result = pipeline.query(question)
        
        if result["success"]:
            # Show top 3 in console, but include all in file
            docs_info = "📚 Retrieved Documents (showing top 3 in console):\n"
            for i, doc in enumerate(result["retrieved_docs"][:3], 1):  # Show top 3
                docs_info += f"  [{i}] {doc['section']} (score: {doc['score']:.4f})\n"
            
            output_lines.append(docs_info)
            print(docs_info)
            
            # Add all chunks to file output
            chunks_section = f"\n📄 ALL RETRIEVED CHUNKS ({result['num_docs']} total):\n"
            chunks_section += "=" * 100 + "\n"
            
            for i, doc in enumerate(result["retrieved_docs"], 1):
                chunks_section += f"\n[CHUNK {i}] Score: {doc['score']:.4f} | Section: {doc['section']}\n"
                chunks_section += f"Document ID: {doc['id']}\n"
                chunks_section += f"Content:\n{doc['text']}\n"
                chunks_section += "-" * 100 + "\n"
            
            output_lines.append(chunks_section)
            
            answer_section = f"\n✅ GENERATED ANSWER (based on {result['num_docs']} documents):\n"
            answer_section += "=" * 100 + "\n"
            answer_section += result["answer"] + "\n"
            answer_section += "=" * 100 + "\n"
            
            output_lines.append(answer_section)
            print(answer_section)
        else:
            error_msg = "❌ Failed to generate answer:\n" + result["answer"] + "\n"
            output_lines.append(error_msg)
            print(error_msg)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(output_lines)
            print(f"\n💾 Output saved to: {output_file}")
    
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}\n"
        print(error_msg)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)


if __name__ == "__main__":
    generate_answer()
