#!/usr/bin/env python3
"""
Test script for the Multimodal QA Agent API
Tests 3 different image-question pairs as requested in the assignment
"""

import requests
import json
import time

# API Configuration
BASE_URL = "http://localhost:5000"
TEST_CASES = [
    {
        "name": "NASA Webb Space Telescope",
        "image_url": "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png",
        "question": "What celestial objects and phenomena can you identify in this space telescope image?",
        "expected_keywords": ["stars", "galaxies", "nebula", "cosmic", "space"]
    },
    {
        "name": "Books and Coffee Scene",
        "image_url": "https://images.unsplash.com/photo-1541963463532-d68292c34d19?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "question": "Describe the objects in this image and what activity might be taking place here.",
        "expected_keywords": ["books", "coffee", "reading", "study", "table"]
    },
    {
        "name": "Golden Retriever Dog",
        "image_url": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
        "question": "What breed is this dog and what are its visible characteristics?",
        "expected_keywords": ["golden retriever", "dog", "fur", "breed", "characteristics"]
    }
]

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_analyze_endpoint(test_case):
    """Test the analyze endpoint with a specific test case"""
    print(f"\n📸 Testing: {test_case['name']}")
    print(f"🔗 Image URL: {test_case['image_url']}")
    print(f"❓ Question: {test_case['question']}")
    
    payload = {
        "question": test_case["question"],
        "image_url": test_case["image_url"]
    }
    
    try:
        print("⏳ Sending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏰ Response time: {response_time:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("success"):
                print("✅ Request successful")
                print(f"🤖 Model used: {data.get('model_used', 'Unknown')}")
                print(f"🔄 Fallback used: {data.get('fallback_used', False)}")
                print(f"📝 Response length: {len(data.get('response', ''))} characters")
                print(f"💬 Response preview: {data.get('response', '')[:200]}...")
                
                # Check for expected keywords
                response_text = data.get('response', '').lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw.lower() in response_text]
                
                print(f"🔍 Keywords found: {found_keywords}")
                print(f"📊 Relevance score: {len(found_keywords)}/{len(test_case['expected_keywords'])}")
                
                return {
                    "success": True,
                    "response_time": response_time,
                    "model_used": data.get('model_used'),
                    "fallback_used": data.get('fallback_used'),
                    "response": data.get('response'),
                    "keywords_found": found_keywords,
                    "relevance_score": len(found_keywords) / len(test_case['expected_keywords'])
                }
            else:
                print(f"❌ API returned success=False: {data.get('error', 'Unknown error')}")
                return {"success": False, "error": data.get('error')}
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {"success": False, "error": str(e)}

def generate_test_report(results):
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("📊 MULTIMODAL QA AGENT - TEST REPORT")
    print("="*60)
    
    successful_tests = sum(1 for r in results if r.get("success", False))
    total_tests = len(results)
    
    print(f"✅ Tests passed: {successful_tests}/{total_tests}")
    print(f"⏰ Average response time: {sum(r.get('response_time', 0) for r in results if r.get('success')) / max(successful_tests, 1):.2f}s")
    
    # Model usage statistics
    vision_model_uses = sum(1 for r in results if r.get('model_used') == 'grok-2-vision-latest')
    fallback_uses = sum(1 for r in results if r.get('fallback_used', False))
    
    print(f"🤖 Vision model uses: {vision_model_uses}")
    print(f"🔄 Fallback uses: {fallback_uses}")
    
    # Individual test results
    print("\n📋 Individual Test Results:")
    for i, (test_case, result) in enumerate(zip(TEST_CASES, results)):
        print(f"\n{i+1}. {test_case['name']}")
        if result.get("success"):
            print(f"   ✅ Status: PASSED")
            print(f"   ⏰ Time: {result.get('response_time', 0):.2f}s")
            print(f"   🤖 Model: {result.get('model_used', 'Unknown')}")
            print(f"   📊 Relevance: {result.get('relevance_score', 0):.2%}")
            print(f"   🔍 Keywords: {result.get('keywords_found', [])}")
        else:
            print(f"   ❌ Status: FAILED")
            print(f"   🚫 Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "="*60)
    print("🎯 TESTING COMPLETED")
    print("="*60)

def main():
    """Main test function"""
    print("🚀 Starting Multimodal QA Agent API Tests")
    print("="*50)
    
    # Test health endpoint first
    if not test_health_endpoint():
        print("❌ Health check failed. Make sure the server is running on http://localhost:5000")
        return
    
    # Run tests for each case
    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n🧪 Test {i}/{len(TEST_CASES)}")
        result = test_analyze_endpoint(test_case)
        results.append(result)
        
        # Add delay between requests to be respectful to the API
        if i < len(TEST_CASES):
            print("⏳ Waiting 2 seconds before next test...")
            time.sleep(2)
    
    # Generate final report
    generate_test_report(results)

if __name__ == "__main__":
    main() 