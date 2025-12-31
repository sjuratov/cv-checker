#!/usr/bin/env python3
"""
Quick verification script for Phase 3 implementation.

Run this to verify all imports work correctly.
"""

import sys


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing Phase 3 imports...")
    print("-" * 60)

    tests = []

    # Test 1: FastAPI
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        tests.append(False)

    # Test 2: Pydantic
    try:
        import pydantic
        print(f"✅ Pydantic {pydantic.__version__}")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        tests.append(False)

    # Test 3: Azure Identity
    try:
        import azure.identity
        print("✅ Azure Identity")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Azure Identity import failed: {e}")
        tests.append(False)

    # Test 4: Microsoft Agent Framework - Core
    try:
        import agent_framework
        print("✅ Microsoft Agent Framework Core")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Microsoft Agent Framework Core import failed: {e}")
        tests.append(False)

    # Test 5: Microsoft Agent Framework - Azure AI
    try:
        from agent_framework.azure import AzureOpenAIChatClient
        print("✅ Microsoft Agent Framework Azure AI")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Microsoft Agent Framework Azure AI import failed: {e}")
        tests.append(False)

    # Test 6: Application imports
    try:
        from app.config import get_settings
        print("✅ App config")
        tests.append(True)
    except ImportError as e:
        print(f"❌ App config import failed: {e}")
        tests.append(False)

    # Test 7: Agent imports
    try:
        from app.agents.job_parser import JobParserAgent
        from app.agents.cv_parser import CVParserAgent
        from app.agents.analyzer import HybridScoringAgent
        from app.agents.report_generator import ReportGeneratorAgent
        from app.agents.orchestrator import CVCheckerOrchestrator
        print("✅ All agent modules")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Agent import failed: {e}")
        tests.append(False)

    # Test 8: Utils
    try:
        from app.utils.azure_openai import get_openai_client
        print("✅ Azure OpenAI utils")
        tests.append(True)
    except ImportError as e:
        print(f"❌ Azure OpenAI utils import failed: {e}")
        tests.append(False)

    print("-" * 60)

    if all(tests):
        print(f"✅ All {len(tests)} import tests passed!")
        print("\nPhase 3 implementation is ready for testing.")
        print("\nNext steps:")
        print("1. Configure Azure OpenAI credentials in .env")
        print("2. Start the server: uv run uvicorn app.main:app --reload")
        print("3. Test health check: curl http://localhost:8000/api/v1/health")
        print("4. See TESTING_GUIDE.md for full testing instructions")
        return 0
    else:
        failed = len([t for t in tests if not t])
        print(f"❌ {failed}/{len(tests)} import tests failed!")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(test_imports())
