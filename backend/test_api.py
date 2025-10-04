#!/usr/bin/env python3
"""
Test script for the RAG API functions.
Demonstrates both JSON output and debug file generation.
"""

from generation.api import query_rag_json, query_rag_debug
import json


def test_json_function():
    """Test the clean JSON output function."""
    print("🔬 Testing JSON Function")
    print("=" * 50)
    
    question = "Which genes are implicated in bisphosphonate-mediated muscle improvements?"
    result = query_rag_json(question)
    
    print(f"Question: {question}")
    print(f"Confident: {result['confident']}")
    print(f"Citations: {len(result['citations'])}")
    print(f"Answer length: {len(result['answer_markdown'])} characters")
    
    if result['citations']:
        print("\nFirst citation:")
        print(f"  ID: {result['citations'][0]['id']}")
        print(f"  URL: {result['citations'][0]['url']}")
        print(f"  Relevant: {result['citations'][0]['why_relevant']}")
    
    print("\nAnswer preview:")
    print(result['answer_markdown'][:200] + "..." if len(result['answer_markdown']) > 200 else result['answer_markdown'])
    print()


def test_debug_function():
    """Test the debug file generation function."""
    print("🐛 Testing Debug Function")
    print("=" * 50)
    
    question = "How do astronauts grow food in space?"
    debug_file = query_rag_debug(question, "debug_space_food.txt")
    
    print(f"Question: {question}")
    print(f"Debug file: {debug_file}")
    
    # Show file size
    import os
    if os.path.exists(debug_file):
        size = os.path.getsize(debug_file)
        print(f"File size: {size:,} bytes")
    
    print()


if __name__ == "__main__":
    test_json_function()
    test_debug_function()
    
    print("✅ API testing complete!")
    print("\nUsage examples:")
    print("  # For integration:")
    print("  from generation.api import query_rag_json")
    print("  result = query_rag_json('Your question here')")
    print()
    print("  # For debugging:")
    print("  from generation.api import query_rag_debug")
    print("  debug_file = query_rag_debug('Your question here')")
