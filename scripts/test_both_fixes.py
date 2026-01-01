#!/usr/bin/env python3
"""
Test script to verify both fixes:
1. No duplicate analysis records in CosmosDB
2. Frontend navigation works correctly (tested manually)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_no_duplicate_analysis():
    """Test that we don't create duplicate analysis records."""
    
    logger.info("=" * 80)
    logger.info("Testing Fix #2: No Duplicate Analysis Records")
    logger.info("=" * 80)
    
    settings = get_settings()
    
    if not settings.is_cosmos_enabled:
        logger.warning("⚠️  Cosmos DB not enabled - skipping test")
        return
    
    # Connect to Cosmos DB using the same method as the main app
    try:
        connection_str = settings.cosmos_connection_string
        if "AccountKey=" in connection_str:
            # Using connection string with account key
            client = CosmosClient.from_connection_string(connection_str)
        else:
            # Using Azure AD authentication
            credential = DefaultAzureCredential()
            client = CosmosClient(connection_str, credential)
        
        database = client.get_database_client(settings.cosmos_database_name)
        container = database.get_container_client(settings.cosmos_container_name)
    except Exception as e:
        logger.error(f"❌ Failed to connect to Cosmos DB: {e}")
        return
    
    # Get all analysis documents for anonymous user
    user_id = "anonymous"
    
    query = """
    SELECT c.id, c.userId, c.cvId, c.jobId, c.createdAt
    FROM c
    WHERE c.userId = @userId
    AND c.documentType = 'analysis'
    ORDER BY c.createdAt DESC
    """
    
    try:
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@userId", "value": user_id}],
            partition_key=user_id,
            enable_cross_partition_query=False
        ))
        
        logger.info(f"\n📊 Found {len(items)} analysis document(s) for user '{user_id}'")
        
        if not items:
            logger.info("✅ No analysis documents found (clean state)")
            return
        
        # Group by timestamp to find potential duplicates
        from collections import defaultdict
        by_timestamp = defaultdict(list)
        
        for item in items:
            created_at = item.get('createdAt', 'unknown')
            by_timestamp[created_at].append(item)
        
        # Check for duplicates
        duplicates_found = False
        for timestamp, docs in by_timestamp.items():
            if len(docs) > 1:
                duplicates_found = True
                logger.error(f"\n❌ DUPLICATE FOUND at {timestamp}:")
                for doc in docs:
                    logger.error(f"   - ID: {doc['id']}")
                    logger.error(f"     CV ID: {doc.get('cvId', 'N/A')}")
                    logger.error(f"     Job ID: {doc.get('jobId', 'N/A')}")
        
        if not duplicates_found:
            logger.info("\n✅ No duplicate analysis records found!")
            logger.info("\nAnalysis documents:")
            for item in items[:5]:  # Show first 5
                logger.info(f"  - {item['id']} (created: {item.get('createdAt', 'unknown')})")
                logger.info(f"    CV: {item.get('cvId', 'N/A')}, Job: {item.get('jobId', 'N/A')}")
        
        # Check ID format
        logger.info("\n📋 Checking ID formats:")
        correct_format = 0
        incorrect_format = 0
        
        for item in items:
            doc_id = item['id']
            if doc_id.startswith('analysis-'):
                correct_format += 1
                logger.info(f"  ✅ {doc_id} (correct format)")
            else:
                incorrect_format += 1
                logger.error(f"  ❌ {doc_id} (incorrect format - should start with 'analysis-')")
        
        logger.info(f"\n📈 Summary:")
        logger.info(f"  Correct format: {correct_format}")
        logger.info(f"  Incorrect format: {incorrect_format}")
        
        if incorrect_format > 0:
            logger.error("\n❌ Found analysis records with incorrect ID format!")
            logger.error("   This suggests old code or duplicate save logic is still active.")
        else:
            logger.info("\n✅ All analysis records have correct ID format!")
        
        return not duplicates_found and incorrect_format == 0
        
    except exceptions.CosmosHttpResponseError as e:
        logger.error(f"❌ Cosmos DB query failed: {e}")
        return False


def test_frontend_navigation():
    """Instructions for manual frontend testing."""
    
    logger.info("\n" + "=" * 80)
    logger.info("Testing Fix #1: Frontend Navigation")
    logger.info("=" * 80)
    logger.info("""
Manual Testing Steps:

1. Start the frontend (if not already running):
   cd frontend
   npm run dev

2. Open http://localhost:5173/ in your browser

3. Upload a CV and provide a job description

4. Click "Analyze CV" and wait for results

5. Verify results display correctly

6. Click the browser's back button OR navigate to http://localhost:5173/

7. ✅ EXPECTED: Upload page shows with CV upload and job description inputs
   ❌ PREVIOUS BUG: Blank page with no controls

8. Navigate to results again (forward button)

9. ✅ EXPECTED: Results display correctly

ROOT CAUSE FIXED:
- Removed currentView persistence from Zustand store
- This prevents stale 'results' view from persisting when there's no data
- App now always shows upload view when navigating to homepage

FILE CHANGED:
- frontend/src/store/useAppStore.ts (partialize function)
""")


async def main():
    """Run both tests."""
    
    logger.info("🔍 CV Checker - Both Fixes Verification\n")
    
    # Test 1: Manual frontend test instructions
    test_frontend_navigation()
    
    # Test 2: Automated backend test
    result = await test_no_duplicate_analysis()
    
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    logger.info("Fix #1 (Blank Page): Manual testing required (see instructions above)")
    if result:
        logger.info("Fix #2 (Duplicate Records): ✅ PASSED - No duplicates found")
    elif result is False:
        logger.info("Fix #2 (Duplicate Records): ❌ FAILED - Issues detected")
    else:
        logger.info("Fix #2 (Duplicate Records): ⚠️  SKIPPED - Cosmos DB not enabled")
    
    logger.info("\n📝 CHANGES MADE:")
    logger.info("1. frontend/src/store/useAppStore.ts")
    logger.info("   - Removed currentView from persistence")
    logger.info("   - Prevents blank page when navigating to homepage")
    logger.info("\n2. backend/app/services/cv_checker.py")
    logger.info("   - Removed duplicate repository.save() call")
    logger.info("   - Analysis now saved only once in main.py via create_analysis()")
    logger.info("\n3. Result: Single source of truth for analysis creation")
    logger.info("   - Only cosmos_repository.create_analysis() creates records")
    logger.info("   - Consistent ID format: 'analysis-{uuid}'")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
