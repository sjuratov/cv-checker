# State Management Fix - Analysis Report

**Date**: January 1, 2026
**Issue**: Frontend persisting old state (CV, Job, History) across restarts

## Investigation Summary

### 1. Frontend State Persistence ✅
**Finding**: The Zustand store is correctly configured with `partialize` to only persist `currentView`:

```typescript
// frontend/src/store/useAppStore.ts:190-194
{
  name: 'cv-checker-storage',
  // Only persist UI preferences, not data
  partialize: (state) => ({
    currentView: state.currentView,
  }),
}
```

**Status**: ✅ **CORRECT** - localStorage only stores UI state, not data

### 2. History Management ❌
**Finding**: History is being populated via `addToHistory()` in the store (in-memory):

```typescript
// frontend/src/store/useAppStore.ts:167-181
addToHistory: (result, cvFilename) =>
  set((state) => {
    const historyEntry: AnalysisHistory = {
      id: result.analysis_id,
      timestamp: new Date().toISOString(),
      cvFilename,
      score: result.overall_score,
      result,
    };

    return {
      history: [historyEntry, ...state.history].slice(0, 10),
    };
  }),
```

**Status**: ❌ **INCORRECT** - This method is adding items to in-memory store instead of relying solely on backend

### 3. Backend Data Model ✅
**Finding**: Backend models correctly have `cvId` and `jobId` fields:

```python
# backend/app/models/cosmos_models.py:103-104
cvId: str = Field(..., description="Reference to CV document ID")
jobId: str = Field(..., description="Reference to job document ID")
```

**Status**: ✅ **CORRECT** - Proper linking exists

### 4. API Integration ✅/❌
**Finding**: 
- ✅ History component correctly fetches from backend via `api.getHistory()`
- ✅ Backend `/api/v1/history` endpoint properly fetches from CosmosDB
- ✅ Backend properly stores CV and Job with IDs during analysis
- ❌ History API doesn't return proper CV filename or Job title (using generic names)

**Status**: ⚠️ **PARTIALLY CORRECT** - Fetching works but data quality needs improvement

## Root Cause Analysis

The user is likely NOT seeing "old state" from localStorage persistence, but rather:

1. **Browser cache/hot reload**: During development, Vite's HMR might preserve state
2. **In-memory history**: The `addToHistory()` method populates history in-memory during the session
3. **Missing data in history response**: The history response shows generic CV/Job names instead of meaningful ones

## Issues to Fix

### Issue 1: In-Memory History Population ❌
**Problem**: `addToHistory()` is being called after analysis, adding items to the in-memory store.

**Solution**: Remove the in-memory history management completely, rely only on backend.

### Issue 2: Generic CV/Job Names in History Response ⚠️
**Problem**: History shows "CV-{id}" and "Job-{id}" instead of meaningful names.

**Solution**: 
- Store CV filename when creating CV document
- Extract job title from content when creating Job document
- Return these in history API response

### Issue 3: State Not Properly Reset on Page Refresh
**Problem**: Even though localStorage is clean, if browser doesn't fully reload, state might persist.

**Solution**: Ensure state is properly initialized as empty on mount.

## Recommended Fixes

### Fix 1: Remove In-Memory History Management
Remove `addToHistory()` calls and the in-memory history array from the store.

### Fix 2: Enhance Backend History Response
Update the `/api/v1/history` endpoint to:
- Return proper CV filename (extract from CV content or store separately)
- Return proper job title (extract from job content or URL)

### Fix 3: Add CV Filename and Job Title to Models
Update data models to store:
- `CVDocument.filename: str` - Original filename
- `JobDocument.title: str` - Extracted job title

### Fix 4: Clear Store Method
Add a method to completely reset the application state.

## Implementation Plan

1. **Backend Changes**:
   - Add `filename` field to `CVDocument`
   - Add `title` field to `JobDocument`
   - Update `create_cv()` to accept filename parameter
   - Update history endpoint to extract and return meaningful names

2. **Frontend Changes**:
   - Remove `addToHistory()` method
   - Remove `history` state from store
   - Add store reset method
   - Update analysis flow to not call `addToHistory()`

3. **API Changes**:
   - Update CV upload flow to send filename
   - Update job submission to extract/store title
