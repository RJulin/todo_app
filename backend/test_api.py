#!/usr/bin/env python3
"""
Simple test script to verify the FastAPI backend is working.
Run this after starting the backend server.
"""

import requests
import json

def test_backend():
    base_url = "http://localhost:8000"
    
    print("Testing FastAPI Backend...")
    print("=" * 40)
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint (/): {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint (/health): {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
            
        print("\n✅ Backend is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"❌ Error testing backend: {e}")

if __name__ == "__main__":
    test_backend() 