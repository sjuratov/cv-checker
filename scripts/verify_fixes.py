#!/usr/bin/env python3
"""
Quick verification that the fixes are in place.
Checks the actual code to ensure changes were applied.
"""

import sys
from pathlib import Path

def check_frontend_fix():
    """Verify the frontend fix is in place."""
    print("=" * 80)
    print("Checking Frontend Fix (Issue #1: Blank Page)")
    print("=" * 80)
    
    file_path = Path(__file__).parent.parent / "frontend/src/store/useAppStore.ts"
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    content = file_path.read_text()
    
    # Check that the old persistence config is NOT present
    if "partialize: (state) => ({" in content and "currentView: state.currentView" in content:
        print("❌ FAILED: Old persistence configuration still present!")
        print("   Expected: partialize: () => ({})")
        print("   Found: Old config with currentView persistence")
        return False
    
    # Check that the new persistence config IS present
    if "partialize: () => ({})" in content:
        print("✅ PASSED: Frontend fix is in place")
        print("   State persistence disabled correctly")
        return True
    else:
        print("⚠️  WARNING: Could not verify the fix")
        print("   Please manually check the partialize configuration")
        return None


def check_backend_fix():
    """Verify the backend fix is in place."""
    print("\n" + "=" * 80)
    print("Checking Backend Fix (Issue #2: Duplicate Records)")
    print("=" * 80)
    
    file_path = Path(__file__).parent.parent / "backend/app/services/cv_checker.py"
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    content = file_path.read_text()
    
    # Check that the duplicate save call is NOT present
    if "await self.repository.save(result)" in content:
        print("❌ FAILED: Duplicate save call still present!")
        print("   Found: await self.repository.save(result)")
        print("   This should be removed from the service layer")
        return False
    
    # Check that we're not saving in the service
    if "analysis_id = await self.repository.save" in content:
        print("❌ FAILED: Repository save still being called!")
        return False
    
    # Verify the analyze_cv method exists and doesn't save
    if "async def analyze_cv(" in content and "return result" in content:
        print("✅ PASSED: Backend fix is in place")
        print("   Duplicate save call removed from service layer")
        return True
    else:
        print("⚠️  WARNING: Could not fully verify the fix")
        return None


def main():
    print("\n🔍 Verifying Both Fixes Are Applied\n")
    
    frontend_ok = check_frontend_fix()
    backend_ok = check_backend_fix()
    
    print("\n" + "=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    results = []
    
    if frontend_ok:
        print("✅ Issue #1 (Blank Page): FIX VERIFIED")
        results.append(True)
    elif frontend_ok is False:
        print("❌ Issue #1 (Blank Page): FIX NOT APPLIED")
        results.append(False)
    else:
        print("⚠️  Issue #1 (Blank Page): VERIFICATION INCONCLUSIVE")
        results.append(None)
    
    if backend_ok:
        print("✅ Issue #2 (Duplicate Records): FIX VERIFIED")
        results.append(True)
    elif backend_ok is False:
        print("❌ Issue #2 (Duplicate Records): FIX NOT APPLIED")
        results.append(False)
    else:
        print("⚠️  Issue #2 (Duplicate Records): VERIFICATION INCONCLUSIVE")
        results.append(None)
    
    print("=" * 80)
    
    if all(r is True for r in results):
        print("\n✅ SUCCESS: All fixes verified!")
        print("\nNext steps:")
        print("1. Test frontend navigation manually")
        print("2. Run an analysis and check CosmosDB for duplicates")
        print("3. Use: ./scripts/test_e2e_both_fixes.sh")
        return 0
    elif any(r is False for r in results):
        print("\n❌ FAILURE: Some fixes not applied correctly")
        print("\nPlease review the changes and try again.")
        return 1
    else:
        print("\n⚠️  WARNING: Could not fully verify all fixes")
        print("\nPlease manually review the changed files.")
        return 2


if __name__ == "__main__":
    sys.exit(main())
