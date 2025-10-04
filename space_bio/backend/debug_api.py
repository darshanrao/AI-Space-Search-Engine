#!/usr/bin/env python3
"""
Debug script to test API endpoints and see detailed error messages.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_thread_creation():
    """Test thread creation with detailed error info."""
    print("Testing thread creation...")
    try:
        payload = {"seed_context": {}}
        response = requests.post(f"{BASE_URL}/api/thread", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure the backend is running.")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"SUCCESS: {response.json()}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("Debug API Test")
    print("="*40)
    
    health_ok = test_health()
    if health_ok:
        test_thread_creation()
    else:
        print("Health check failed. Backend server not running.")
