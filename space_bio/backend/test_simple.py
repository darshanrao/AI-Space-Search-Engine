#!/usr/bin/env python3
"""
Test the simple backend directly.
"""

import requests
import json

def test_simple_backend():
    """Test the simple backend."""
    base_url = "http://localhost:8000"
    
    print("Testing Simple Backend")
    print("=" * 30)
    
    # Test health
    print("1. Testing health...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test thread creation
    print("\n2. Testing thread creation...")
    try:
        response = requests.post(f"{base_url}/api/thread", json={"seed_context": {}})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()}")
        else:
            print(f"ERROR: {response.text}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_simple_backend()
