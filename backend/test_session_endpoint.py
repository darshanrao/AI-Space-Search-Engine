#!/usr/bin/env python3
"""
Test the session endpoint specifically
"""

import requests
import json

def test_session_endpoint():
    base_url = "http://localhost:8000"
    
    print("Testing session endpoint...")
    
    # First, create a session by sending a message
    print("\n1. Creating session with a message...")
    response = requests.post(
        f"{base_url}/api/chat",
        json={
            "message": "Hello, this is a test message",
            "context": {"organism": "C. elegans"}
        },
        headers={
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        session_id = data['session_id']
        print(f"Session ID: {session_id}")
    else:
        print(f"Error: {response.text}")
        return
    
    # Now test the session endpoint
    print(f"\n2. Testing GET /api/session/{session_id}...")
    response = requests.get(
        f"{base_url}/api/session/{session_id}",
        headers={'Origin': 'http://localhost:3000'}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Session ID: {data['session_id']}")
        print(f"Messages count: {len(data['messages'])}")
        print(f"Context: {data['context']}")
        print(f"Created at: {data['created_at']}")
        
        # Show first message
        if data['messages']:
            first_msg = data['messages'][0]
            print(f"First message: {first_msg['role']} - {first_msg['content'][:50]}...")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_session_endpoint()

