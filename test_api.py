#!/usr/bin/env python3
import requests
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("Testing ThreeJS Code Generator API...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error connecting to root: {e}")
        return
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Error connecting to health: {e}")
        return
    
    # Test generate endpoint
    try:
        test_request = {
            "prompt": "Create a simple rotating cube",
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{base_url}/generate",
            headers={"Content-Type": "application/json"},
            json=test_request
        )
        
        print(f"Generate endpoint: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Generated code (first 200 chars):")
            print(result["code"][:200] + "...")
            print("\nExplanation:")
            print(result["explanation"][:100] + "...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error testing generate endpoint: {e}")

if __name__ == "__main__":
    test_api()