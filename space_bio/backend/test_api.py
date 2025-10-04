#!/usr/bin/env python3
"""
Test script for the new RAG Chat API.
"""

import requests
import json

def test_rag_chat_api():
    base_url = "http://localhost:8000"
    
    print("Testing RAG Chat API...")
    
    # Test 1: Health check
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test 2: First chat message
    print("\n2. Testing first chat message...")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "What genes are implicated in bisphosphonate-mediated muscle improvements?",
                "context": {"organism": "C. elegans", "focus": "muscle health"}
            },
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000'
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data['session_id']}")
            print(f"Message: {data['message'][:100]}...")
            
            if data.get('rag_response'):
                rag = data['rag_response']
                print(f"Citations: {len(rag['citations'])}")
                print(f"Context IDs: {len(rag['used_context_ids'])}")
                print(f"Confident: {rag['confident']}")
                
                # Show first citation
                if rag['citations']:
                    citation = rag['citations'][0]
                    print(f"First Citation: {citation['id']}")
            
            session_id = data['session_id']
        else:
            print(f"Error: {response.text}")
            return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test 3: Follow-up message
    print("\n3. Testing follow-up message...")
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={
                "message": "Tell me more about the FOXO pathway",
                "session_id": session_id
            },
            headers={
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000'
            }
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data['message'][:100]}...")
            
            if data.get('rag_response'):
                rag = data['rag_response']
                print(f"Citations: {len(rag['citations'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get session history
    print("\n4. Testing session history...")
    try:
        response = requests.get(
            f"{base_url}/api/session/{session_id}",
            headers={'Origin': 'http://localhost:3000'}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Messages in session: {len(data['messages'])}")
            for i, msg in enumerate(data['messages']):
                print(f"  {i+1}. {msg['role']}: {msg['content'][:50]}...")
                if msg.get('rag_response'):
                    print(f"      Citations: {len(msg['rag_response']['citations'])}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: List all sessions
    print("\n5. Testing session list...")
    try:
        response = requests.get(
            f"{base_url}/api/sessions",
            headers={'Origin': 'http://localhost:3000'}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total sessions: {data['count']}")
            print(f"Session IDs: {data['sessions']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    test_rag_chat_api()
