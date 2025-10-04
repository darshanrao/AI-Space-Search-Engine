#!/usr/bin/env python3
"""
List available Gemini models.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def list_available_models():
    """List all available Gemini models."""
    print("Listing available Gemini models...")
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        return
    
    print(f"SUCCESS: API Key found: {api_key[:10]}...")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # List models
        models = genai.list_models()
        
        print("Available models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"  - {model.name}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    list_available_models()
