#!/usr/bin/env python3
"""
Test script to verify Gemini API connectivity and key.
"""

import os
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables from .env file
load_dotenv()

async def test_gemini_connection():
    """Test Gemini API connection."""
    print("Testing Gemini API connection...")
    
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment variables")
        return False
    
    print(f"SUCCESS: API Key found: {api_key[:10]}...")
    
    try:
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_output_tokens=100
        )
        
        print("SUCCESS: Gemini model initialized successfully")
        
        # Test a simple message
        message = HumanMessage(content="Hello, can you respond with just 'Hi there!'?")
        response = await llm.ainvoke([message])
        
        print(f"SUCCESS: Gemini response: {response.content}")
        return True
        
    except Exception as e:
        print(f"ERROR: Gemini API error: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_connection())
    if result:
        print("\nSUCCESS: Gemini API is working correctly!")
    else:
        print("\nFAILED: Gemini API test failed!")
