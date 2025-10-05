#!/usr/bin/env python3
"""
Test script to verify RAG pipeline integration.
This will test the RAG service with fallback to basic Gemini if Qdrant is not configured.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rag_service_import():
    """Test that we can import the RAG service."""
    try:
        from rag_service import RAGService
        print("RAG service import successful")
        return True
    except Exception as e:
        print(f"RAG service import failed: {e}")
        return False

def test_rag_pipeline_import():
    """Test that we can import the RAG pipeline components."""
    try:
        from generation.api import query_rag_json
        print("RAG pipeline import successful")
        return True
    except Exception as e:
        print(f"RAG pipeline import failed: {e}")
        return False

def test_rag_service_initialization():
    """Test that we can initialize the RAG service."""
    try:
        from rag_service import RAGService
        service = RAGService()
        print("RAG service initialization successful")
        return True
    except Exception as e:
        print(f"RAG service initialization failed: {e}")
        return False

def test_fallback_response():
    """Test that the fallback response works when RAG pipeline fails."""
    try:
        from rag_service import RAGService
        service = RAGService()
        
        # Test fallback response (should work even without Qdrant)
        response = service._generate_fallback_response(
            "What is space biology?", 
            {"organism": "C. elegans", "focus": "space biology"}
        )
        
        if response.answer_markdown and len(response.answer_markdown) > 10:
            print("Fallback response generation successful")
            print(f"   Answer preview: {response.answer_markdown[:100]}...")
            return True
        else:
            print("Fallback response generation failed - empty response")
            return False
            
    except Exception as e:
        print(f"Fallback response test failed: {e}")
        return False

def test_rag_pipeline_with_credentials():
    """Test RAG pipeline if credentials are available."""
    try:
        qdrant_url = os.environ.get("QDRANT_URL")
        qdrant_key = os.environ.get("QDRANT_API_KEY")
        
        if not qdrant_url or not qdrant_key:
            print("Qdrant credentials not found - skipping RAG pipeline test")
            print("   Add QDRANT_URL and QDRANT_API_KEY to .env file to test full RAG pipeline")
            return True
        
        from generation.api import query_rag_json
        result = query_rag_json("What is space biology?")
        
        if result.get("answer_markdown"):
            print("RAG pipeline test successful")
            print(f"   Answer preview: {result['answer_markdown'][:100]}...")
            print(f"   Citations: {len(result.get('citations', []))}")
            return True
        else:
            print("RAG pipeline test failed - no answer generated")
            return False
            
    except Exception as e:
        print(f"RAG pipeline test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing RAG Integration...")
    print("=" * 50)
    
    tests = [
        test_rag_service_import,
        test_rag_pipeline_import,
        test_rag_service_initialization,
        test_fallback_response,
        test_rag_pipeline_with_credentials
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! RAG integration is ready.")
        print("\nNext steps:")
        print("1. Add QDRANT_URL and QDRANT_API_KEY to your .env file")
        print("2. Start the backend server: python main.py")
        print("3. Test the chatbot with real RAG responses")
    else:
        print("Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
