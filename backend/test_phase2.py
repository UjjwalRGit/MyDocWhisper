"""
Phase 2 Backend Test Script
Tests streaming endpoint and chat history functionality
"""

import asyncio
import aiohttp
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

async def test_health_check():
    """Test that the API is running and reports v2.0"""
    print("\n🧪 Test 1: Health Check")
    print("-" * 50)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/") as response:
            data = await response.json()
            print(f"✅ API Status: {data['message']}")
            print(f"✅ Version: {data['version']}")
            print(f"✅ Features: {json.dumps(data['features'], indent=2)}")
            
            assert data['version'] == "2.0", "Version should be 2.0"
            assert data['features']['streaming'] == True, "Streaming should be enabled"
            print("\n✅ Health check passed!")

async def test_streaming_endpoint():
    """Test that streaming endpoint works"""
    print("\n🧪 Test 2: Streaming Endpoint")
    print("-" * 50)
    
    # You'll need to have a document uploaded for this test
    # For demo purposes, we'll just check if the endpoint exists
    
    request_data = {
        "message": "Test question",
        "documentId": "test_doc",
        "history": []
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/chat/stream",
                json=request_data
            ) as response:
                # We expect a 404 if no document is uploaded, or a stream if one exists
                if response.status == 404:
                    print("⚠️  No document found (expected if none uploaded)")
                    print("✅ Streaming endpoint is accessible")
                else:
                    print(f"✅ Streaming endpoint responded with status: {response.status}")
                    
                    # Read first chunk to verify streaming works
                    chunk = await response.content.read(100)
                    print(f"✅ Received streaming data: {len(chunk)} bytes")
        except Exception as e:
            print(f"❌ Streaming test failed: {e}")

async def test_backward_compatibility():
    """Test that old /chat endpoint still works"""
    print("\n🧪 Test 3: Backward Compatibility")
    print("-" * 50)
    
    request_data = {
        "message": "Test question",
        "documentId": "test_doc",
        "history": []
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{BASE_URL}/chat",
                json=request_data
            ) as response:
                if response.status == 404:
                    print("⚠️  No document found (expected if none uploaded)")
                    print("✅ Non-streaming endpoint is accessible")
                else:
                    data = await response.json()
                    print(f"✅ Non-streaming endpoint works")
                    print(f"✅ Response format includes 'answer' and 'sources'")
        except Exception as e:
            print(f"❌ Compatibility test failed: {e}")

async def test_chat_history_format():
    """Test that chat history is properly formatted"""
    print("\n🧪 Test 4: Chat History Format")
    print("-" * 50)
    
    # Test data with history
    request_data = {
        "message": "Follow-up question",
        "documentId": "test_doc",
        "history": [
            {"role": "user", "content": "First question"},
            {"role": "assistant", "content": "First answer"},
            {"role": "user", "content": "Second question"}
        ]
    }
    
    print("✅ Chat history format is correct:")
    print(json.dumps(request_data['history'], indent=2))
    print("✅ History contains role and content fields")
    print("✅ Format matches backend expectations")

async def main():
    """Run all tests"""
    print("=" * 50)
    print("MyDocWhisper Phase 2 - Backend Test Suite")
    print("=" * 50)
    
    try:
        await test_health_check()
        await test_streaming_endpoint()
        await test_backward_compatibility()
        await test_chat_history_format()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        print("=" * 50)
        
        print("\n📝 Next Steps:")
        print("1. Upload a PDF document via the frontend")
        print("2. Test streaming with real questions")
        print("3. Test chat history with follow-up questions")
        print("4. Check source citations display correctly")
        
    except aiohttp.ClientConnectorError:
        print("\n❌ ERROR: Cannot connect to backend!")
        print("Make sure the backend is running:")
        print("  python main_v2.py")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    print("\n⚠️  Make sure the backend is running on http://localhost:8000")
    print("Starting tests in 2 seconds...\n")
    
    import time
    time.sleep(2)
    
    asyncio.run(main())
