"""
Test script for the LangChain agent reasoning system.
This tests whether the agent correctly decides when to use RAG vs. its own knowledge.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generation.agent_service import agent_service
from models import RAGResponse


def test_agent_reasoning():
    """Test the agent's reasoning capabilities."""
    
    print("🤖 Testing LangChain Agent Reasoning System")
    print("=" * 60)
    
    # Test cases that should NOT use RAG (general knowledge)
    general_knowledge_tests = [
        "What is photosynthesis?",
        "What is DNA?",
        "What are the basic principles of biology?",
        "What is gravity?",
        "Hello, how are you?"
    ]
    
    # Test cases that SHOULD use RAG (specific space biology research)
    space_biology_tests = [
        "What are the effects of microgravity on C. elegans muscle development?",
        "What research has been done on bone loss in astronauts?",
        "How does space radiation affect plant growth?",
        "What are the latest findings on space biology experiments?",
        "Tell me about specific NASA space biology research papers"
    ]
    
    print("\n📚 Testing General Knowledge Questions (should NOT use RAG):")
    print("-" * 60)
    
    for i, question in enumerate(general_knowledge_tests, 1):
        print(f"\n{i}. Question: {question}")
        print("Expected: Answer from LLM knowledge (no RAG)")
        
        try:
            response = agent_service.generate_answer(
                question=question,
                context={"organism": "General", "focus": "biology"},
                conversation_history=[]
            )
            
            print(f"Answer: {response.answer_markdown[:200]}...")
            print(f"Citations: {len(response.citations)} found")
            print(f"Confidence: {response.confidence_score}%")
            
            # Check if RAG was used (indicated by citations)
            if response.citations:
                print("⚠️  WARNING: RAG was used for general knowledge question")
            else:
                print("✅ Correct: Used LLM knowledge only")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n\n🚀 Testing Space Biology Questions (should use RAG):")
    print("-" * 60)
    
    for i, question in enumerate(space_biology_tests, 1):
        print(f"\n{i}. Question: {question}")
        print("Expected: Answer using RAG search")
        
        try:
            response = agent_service.generate_answer(
                question=question,
                context={"organism": "C. elegans", "focus": "space biology"},
                conversation_history=[]
            )
            
            print(f"Answer: {response.answer_markdown[:200]}...")
            print(f"Citations: {len(response.citations)} found")
            print(f"Confidence: {response.confidence_score}%")
            
            # Check if RAG was used
            if response.citations:
                print("✅ Correct: Used RAG search")
                print(f"Sources: {response.citations[:2]}...")  # Show first 2 sources
            else:
                print("⚠️  WARNING: RAG was not used for specific research question")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n\n🔄 Testing Follow-up Questions:")
    print("-" * 60)
    
    # Test conversation context
    conversation_history = [
        ("user", "What are the effects of microgravity on C. elegans?"),
        ("assistant", "Based on research, microgravity affects C. elegans muscle development...")
    ]
    
    followup_questions = [
        "What about bone development?",
        "Can you tell me more about muscle atrophy?",
        "What is the mechanism behind these effects?"
    ]
    
    for i, question in enumerate(followup_questions, 1):
        print(f"\n{i}. Follow-up: {question}")
        print("Expected: May use context or RAG depending on specificity")
        
        try:
            response = agent_service.generate_answer(
                question=question,
                context={"organism": "C. elegans", "focus": "space biology"},
                conversation_history=conversation_history
            )
            
            print(f"Answer: {response.answer_markdown[:200]}...")
            print(f"Citations: {len(response.citations)} found")
            print(f"Confidence: {response.confidence_score}%")
            
            if response.citations:
                print("✅ Used RAG for detailed follow-up")
            else:
                print("✅ Used context for general follow-up")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 Agent reasoning test completed!")
    print("The agent should intelligently decide when to use RAG vs. its own knowledge.")


if __name__ == "__main__":
    test_agent_reasoning()
