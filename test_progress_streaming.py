#!/usr/bin/env python3
"""
Test script for progress tracking streaming endpoint.
Tests the /api/v1/analyze/stream endpoint to verify progress updates.
"""

import asyncio
import json
import sys

import aiohttp


async def test_streaming_endpoint():
    """Test the streaming analysis endpoint."""
    url = "http://localhost:8000/api/v1/analyze/stream"
    
    # Sample test data
    payload = {
        "cv_markdown": """# John Doe
Software Engineer

## Experience
- 5 years of Python development
- 3 years of FastAPI and React
- Strong background in AI/ML

## Education
- BS in Computer Science
""",
        "cv_filename": "john_doe.md",
        "job_description": """We are looking for a Senior Software Engineer with:
- 5+ years of Python experience
- Experience with FastAPI
- React/TypeScript skills
- Knowledge of AI/ML systems
""",
        "source_type": "manual"
    }
    
    print("🚀 Testing streaming analysis endpoint...")
    print(f"📍 URL: {url}")
    print("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"❌ Error: HTTP {response.status}")
                    text = await response.text()
                    print(f"Response: {text}")
                    return False
                
                print(f"✅ Connection established (HTTP {response.status})")
                print("=" * 60)
                print("\n📊 Progress Updates:\n")
                
                step_count = 0
                result_received = False
                
                # Read streaming response
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    if not line_str:
                        continue
                    
                    try:
                        chunk = json.loads(line_str)
                        
                        if chunk.get("type") == "progress":
                            step = chunk.get("step")
                            total = chunk.get("total_steps")
                            message = chunk.get("message")
                            status = chunk.get("status")
                            
                            step_count += 1
                            
                            # Print progress update
                            if status == "in_progress":
                                print(f"⏳ Step {step}/{total}: {message}")
                            elif status == "completed":
                                print(f"✅ Step {step}/{total}: {message}")
                            
                        elif chunk.get("type") == "result":
                            result_received = True
                            data = chunk.get("data", {})
                            score = data.get("overall_score")
                            analysis_id = data.get("analysis_id")
                            
                            print("\n" + "=" * 60)
                            print("🎯 Final Result:")
                            print(f"   Analysis ID: {analysis_id}")
                            print(f"   Overall Score: {score}/100")
                            print("=" * 60)
                            
                        elif chunk.get("type") == "error":
                            print(f"\n❌ Error: {chunk.get('message')}")
                            return False
                            
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Failed to parse chunk: {line_str[:100]}...")
                        print(f"   Error: {e}")
                
                # Verify we got all expected updates
                print(f"\n📈 Summary:")
                print(f"   Progress updates received: {step_count}")
                print(f"   Result received: {result_received}")
                
                if result_received and step_count >= 4:
                    print("\n✅ Test PASSED - All progress updates and result received!")
                    return True
                else:
                    print(f"\n❌ Test FAILED - Missing updates or result")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"\n❌ Connection Error: {e}")
        print("   Make sure the backend is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    print("\n" + "=" * 60)
    print("  Progress Tracking Streaming Test")
    print("=" * 60 + "\n")
    
    success = await test_streaming_endpoint()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed!")
        sys.exit(0)
    else:
        print("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
