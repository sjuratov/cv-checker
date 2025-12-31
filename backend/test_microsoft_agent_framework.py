#!/usr/bin/env python3
"""
Test script to verify Microsoft Agent Framework implementation.

This script creates a simple agent and tests the workflow.
"""

import asyncio
import os
from azure.identity import DefaultAzureCredential
from agent_framework.azure import AzureOpenAIChatClient


async def test_microsoft_agent_framework():
    """Test basic Microsoft Agent Framework functionality."""
    
    print("=" * 60)
    print("Testing Microsoft Agent Framework Implementation")
    print("=" * 60)
    
    # Check environment variables
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4-1")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    
    if not endpoint:
        print("❌ AZURE_OPENAI_ENDPOINT not set")
        print("Please configure your .env file with Azure OpenAI credentials")
        return False
    
    print(f"✅ Endpoint: {endpoint}")
    print(f"✅ Deployment: {deployment}")
    print(f"✅ API Version: {api_version}")
    print()
    
    try:
        # Create credential
        print("Creating DefaultAzureCredential...")
        credential = DefaultAzureCredential()
        print("✅ Credential created")
        print()
        
        # Create client
        print("Creating AzureOpenAIChatClient...")
        client = AzureOpenAIChatClient(
            credential=credential,
            endpoint=endpoint,
            deployment_name=deployment,
            api_version=api_version,
        )
        print("✅ Client created successfully")
        print()
        
        # Create a test agent
        print("Creating test agent...")
        test_agent = client.create_agent(
            name="TestAgent",
            instructions="You are a helpful assistant. Respond concisely.",
        )
        print("✅ Agent created successfully")
        print()
        
        # Test agent execution
        print("Running test agent with simple prompt...")
        response = await test_agent.run("Say 'Hello from Microsoft Agent Framework!'")
        response_text = response.content if hasattr(response, 'content') else str(response)
        print(f"✅ Agent response: {response_text[:100]}...")
        print()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("Microsoft Agent Framework is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print()
        print("Common issues:")
        print("1. Check AZURE_OPENAI_ENDPOINT is correct")
        print("2. Ensure you're authenticated (az login or service principal)")
        print("3. Verify RBAC permissions on the Azure OpenAI resource")
        print("4. Check deployment name matches your Azure OpenAI deployment")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_microsoft_agent_framework())
    exit(0 if success else 1)
