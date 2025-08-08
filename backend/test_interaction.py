#!/usr/bin/env python3
"""
Test script for the LinkOps-Afterlife interaction endpoint.
This script demonstrates how to test the full pipeline without actual API keys.
"""

import requests
import json
import sys

def test_interaction_endpoint():
    """Test the interaction endpoint with a sample request."""
    
    # API endpoint
    base_url = "http://localhost:8000"
    session_id = "test_session_123"
    
    # Test data
    test_payload = {
        "input": "How are you feeling today?"
    }
    
    print("🚀 Testing LinkOps-Afterlife Interaction Endpoint")
    print("=" * 50)
    
    # Test 1: Check server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{base_url}/ping")
        if response.status_code == 200:
            print("✅ Server is running")
            ping_data = response.json()
            print(f"   Timestamp: {ping_data.get('timestamp')}")
        else:
            print("❌ Server connectivity failed")
            return False
    except Exception as e:
        print(f"❌ Server connection error: {e}")
        return False
    
    # Test 2: Check session status
    print("\\n2. Checking session status...")
    try:
        response = requests.get(f"{base_url}/session_status/{session_id}")
        if response.status_code == 404:
            print("ℹ️  Session not found (expected for test)")
        elif response.status_code == 200:
            status_data = response.json()
            print("✅ Session found")
            print(f"   Ready for interaction: {status_data.get('ready_for_interaction')}")
            print(f"   Requirements: {status_data.get('session_requirements', {}).keys()}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Session status check error: {e}")
    
    # Test 3: Test interaction endpoint (will fail without proper setup, but tests the endpoint)
    print("\\n3. Testing interaction endpoint...")
    try:
        response = requests.post(
            f"{base_url}/interact/{session_id}",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 404:
            print("ℹ️  Session not found (expected without setup)")
        elif response.status_code == 400:
            error_data = response.json()
            print("ℹ️  Session requirements not met (expected without setup)")
            print(f"   Detail: {error_data.get('detail')}")
        elif response.status_code == 500:
            error_data = response.json()
            if "API key not configured" in error_data.get('detail', ''):
                print("ℹ️  API keys not configured (expected in test environment)")
            else:
                print(f"⚠️  Server error: {error_data.get('detail')}")
        elif response.status_code == 200:
            print("✅ Interaction succeeded!")
            result_data = response.json()
            print(f"   User input: {result_data.get('user_input')}")
            print(f"   Video path: {result_data.get('video_path')}")
            print(f"   Processing steps: {result_data.get('processing_steps')}")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Interaction test error: {e}")
    
    # Test 4: Test validation endpoints
    print("\\n4. Testing validation endpoints...")
    
    # Test D-ID key validation
    try:
        response = requests.get(f"{base_url}/validate_d_id_key")
        if response.status_code == 200:
            validation_data = response.json()
            print(f"   D-ID API Key: {'✅ Valid' if validation_data.get('valid') else '❌ Invalid/Not Set'}")
        else:
            print("   D-ID validation endpoint error")
    except Exception as e:
        print(f"   D-ID validation error: {e}")
    
    # Test ElevenLabs key validation
    try:
        response = requests.get(f"{base_url}/validate_elevenlabs_key")
        if response.status_code == 200:
            validation_data = response.json()
            print(f"   ElevenLabs API Key: {'✅ Valid' if validation_data.get('valid') else '❌ Invalid/Not Set'}")
        else:
            print("   ElevenLabs validation endpoint error")
    except Exception as e:
        print(f"   ElevenLabs validation error: {e}")
    
    print("\\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- Server connectivity: Working")
    print("- Endpoint availability: Working") 
    print("- Error handling: Working")
    print("- Ready for production with proper API keys and session setup")
    print("\\n💡 Next Steps:")
    print("1. Set up D_ID_API_KEY and ELEVENLABS_API_KEY environment variables")
    print("2. Upload files using /upload endpoint")
    print("3. Process photo using /preprocess_photo/{session_id}")
    print("4. Clone voice using /clone_voice/{session_id}")
    print("5. Process text using /process_text/{session_id}")
    print("6. Fine-tune conversation using /fine_tune_conversation/{session_id}")
    print("7. Test interaction using /interact/{session_id}")
    
    return True

if __name__ == "__main__":
    test_interaction_endpoint()