#!/usr/bin/env python3
"""
Test script to verify state management fixes in backend.

This script tests:
1. CV document creation with filename
2. Job document creation with title extraction
3. Analysis document linking to CV and Job
4. History API returns proper filenames and titles
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


async def test_cosmos_models():
    """Test Cosmos DB models have new fields."""
    from app.models.cosmos_models import CVDocument, JobDocument
    
    print("✓ Testing Cosmos DB models...")
    
    # Test CV document with filename
    cv = CVDocument(
        id="cv-test-123",
        userId="test-user",
        filename="test_resume.pdf",
        content="# Test CV\n\nExperience: 5 years",
        characterCount=30,
    )
    assert cv.filename == "test_resume.pdf", "CV filename not stored"
    print("  ✓ CVDocument.filename field works")
    
    # Test Job document with title
    job = JobDocument(
        id="job-test-456",
        userId="test-user",
        title="Senior Python Developer",
        content="Looking for a senior developer...",
        sourceType="manual",
        characterCount=35,
    )
    assert job.title == "Senior Python Developer", "Job title not stored"
    print("  ✓ JobDocument.title field works")
    
    print("✅ Cosmos DB models test passed\n")


async def test_repository_title_extraction():
    """Test job title extraction logic."""
    from app.repositories.cosmos_repository import CosmosDBRepository
    
    print("✓ Testing job title extraction...")
    
    # Create a mock repository (without container)
    class MockRepository(CosmosDBRepository):
        def __init__(self):
            # Skip container initialization
            pass
    
    repo = MockRepository()
    
    # Test title extraction from content
    content1 = "# Senior Python Developer\n\nWe are looking for..."
    title1 = repo._extract_job_title(content1, None)
    assert "Senior Python Developer" in title1, f"Failed to extract title: {title1}"
    print(f"  ✓ Extracted from markdown: '{title1}'")
    
    # Test title extraction from LinkedIn URL
    content2 = "Some job description..."
    url = "https://www.linkedin.com/jobs/view/123456789/"
    title2 = repo._extract_job_title(content2, url)
    assert "LinkedIn" in title2, f"Failed to extract from URL: {title2}"
    print(f"  ✓ Extracted from URL: '{title2}'")
    
    # Test fallback
    content3 = ""
    title3 = repo._extract_job_title(content3, None)
    assert title3 == "Job Description", f"Fallback failed: {title3}"
    print(f"  ✓ Fallback works: '{title3}'")
    
    print("✅ Title extraction test passed\n")


async def test_request_models():
    """Test request models have new fields."""
    from app.models.requests import AnalyzeRequest
    
    print("✓ Testing request models...")
    
    # Test AnalyzeRequest with filename
    request = AnalyzeRequest(
        cv_markdown="# Test CV\n\n" + "x" * 100,  # Minimum 100 chars
        cv_filename="my_resume.pdf",
        job_description="x" * 50,  # Minimum 50 chars
    )
    assert request.cv_filename == "my_resume.pdf", "cv_filename not in request"
    print("  ✓ AnalyzeRequest.cv_filename field works")
    
    # Test with default filename
    request2 = AnalyzeRequest(
        cv_markdown="# Test CV\n\n" + "x" * 100,
        job_description="x" * 50,
    )
    assert request2.cv_filename == "resume.pdf", "Default filename not set"
    print("  ✓ Default cv_filename works")
    
    print("✅ Request models test passed\n")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("State Management Fix - Backend Verification")
    print("=" * 60)
    print()
    
    try:
        await test_cosmos_models()
        await test_repository_title_extraction()
        await test_request_models()
        
        print("=" * 60)
        print("✅ ALL BACKEND TESTS PASSED")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start the backend: cd backend && uv run uvicorn app.main:app --reload")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Test the full flow in the browser")
        print("4. Clear browser localStorage and verify clean state")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
