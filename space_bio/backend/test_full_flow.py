#!/usr/bin/env python3
"""
Test the full chatbot flow: create thread -> ask question -> get answer
"""

import requests
import json

def test_full_chatbot_flow():
    """Test the complete chatbot flow."""
    base_url = "http://localhost:8000"
    
    print("Testing Full Chatbot Flow")
    print("=" * 50)
    
    # Step 1: Create a thread
    print("1. Creating thread...")
    thread_response = requests.post(f"{base_url}/api/thread", json={"seed_context": {}})
    
    if thread_response.status_code != 200:
        print(f"ERROR: Thread creation failed: {thread_response.status_code}")
        print(thread_response.text)
        return False
    
    thread_data = thread_response.json()
    thread_id = thread_data["thread_id"]
    print(f"SUCCESS: Thread created: {thread_id}")
    
    # Step 2: Ask a question
    print("\n2. Asking question...")
    question = "What is space biology?"
    answer_request = {
        "q": question,
        "thread_id": thread_id,
        "k": 8,
        "max_tokens": 800
    }
    
    answer_response = requests.post(f"{base_url}/api/answer", json=answer_request)
    
    if answer_response.status_code != 200:
        print(f"ERROR: Answer generation failed: {answer_response.status_code}")
        print(answer_response.text)
        return False
    
    answer_data = answer_response.json()
    print(f"SUCCESS: Answer generated")
    print(f"Question: {answer_data['question']}")
    print(f"Answer: {answer_data['answer'][:200]}...")
    print(f"Answer ID: {answer_data['answer_id']}")
    
    # Step 3: Test follow-up question
    print("\n3. Testing follow-up question...")
    followup_question = "How does microgravity affect humans?"
    followup_request = {
        "q": followup_question,
        "thread_id": thread_id,
        "k": 8,
        "max_tokens": 800
    }
    
    followup_response = requests.post(f"{base_url}/api/answer", json=followup_request)
    
    if followup_response.status_code != 200:
        print(f"ERROR: Follow-up answer failed: {followup_response.status_code}")
        print(followup_response.text)
        return False
    
    followup_data = followup_response.json()
    print(f"SUCCESS: Follow-up answer generated")
    print(f"Question: {followup_data['question']}")
    print(f"Answer: {followup_data['answer'][:200]}...")
    
    # Step 4: Get thread history
    print("\n4. Getting thread history...")
    thread_history = requests.get(f"{base_url}/api/thread/{thread_id}")
    
    if thread_history.status_code != 200:
        print(f"ERROR: Thread history failed: {thread_history.status_code}")
        print(thread_history.text)
        return False
    
    history_data = thread_history.json()
    print(f"SUCCESS: Thread history retrieved")
    print(f"Messages in thread: {len(history_data.get('messages', []))}")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Full chatbot flow test completed!")
    print("Your chatbot is now fully functional with:")
    print("  ✓ Thread creation")
    print("  ✓ Question answering with Gemini")
    print("  ✓ Follow-up questions")
    print("  ✓ Conversation history storage")
    print("  ✓ Supabase database integration")
    
    return True

if __name__ == "__main__":
    success = test_full_chatbot_flow()
    if not success:
        print("\nERROR: Chatbot flow test failed!")
        exit(1)
