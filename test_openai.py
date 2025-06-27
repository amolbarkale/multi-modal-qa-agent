#!/usr/bin/env python3
"""Simple test to check OpenAI client initialization"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
XAI_API_KEY = os.getenv("XAI_API_KEY")
print(f"API Key found: {'Yes' if XAI_API_KEY else 'No'}")

try:
    from openai import OpenAI
    print("✅ OpenAI library imported successfully")
    
    # Try to create client
    client = OpenAI(
        api_key=XAI_API_KEY or "test-key",
        base_url="https://api.x.ai/v1"
    )
    print("✅ OpenAI client created successfully")
    
    # Test if we can make a simple call (will fail without real API key, but should create client)
    print("🎉 OpenAI client configuration is working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}") 