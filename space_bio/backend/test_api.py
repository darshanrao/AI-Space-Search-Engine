#!/usr/bin/env python3
"""
Simple test script to verify API endpoints are working.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_create_thread():
    """Test thread creation endpoint."""
    print("\nTesting thread creation...")
    payload = {"seed_context": {}}
    response = requests.post(
        f"{BASE_URL}/api/thread",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        return data.get("thread_id")
    else:
        print(f"Error: {response.text}")
        return None

def test_search():
    """Test search endpoint."""
    print("\nTesting search endpoint...")
    payload = {
        "q": "space biology",
        "filters": {},
        "limit": 10,
        "offset": 0,
        "thread_id": None
    }
    response = requests.post(
        f"{BASE_URL}/api/search",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_answer(thread_id):
    """Test answer generation endpoint."""
    print(f"\nTesting answer generation with thread_id: {thread_id}")
    payload = {
        "q": "What is space biology?",
        "thread_id": thread_id,
        "k": 8,
        "max_tokens": 800
    }
    response = requests.post(
        f"{BASE_URL}/api/answer",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

if __name__ == "__main__":
    print("Testing Space Bio API endpoints...")
    
    # Test health
    if not test_health():
        print("Health check failed!")
        exit(1)
    
    # Test thread creation
    thread_id = test_create_thread()
    if not thread_id:
        print("Thread creation failed!")
        exit(1)
    
    # Test search
    if not test_search():
        print("Search test failed!")
        exit(1)
    
    # Test answer generation
    if not test_answer(thread_id):
        print("Answer generation failed!")
        exit(1)
    
    print("\n✅ All tests passed! The API is working correctly.")
