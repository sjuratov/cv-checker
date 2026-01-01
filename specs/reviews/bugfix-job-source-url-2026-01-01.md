# Bug Fix Review: Job Source URL Display

**Date:** January 1, 2026  
**Type:** Bug Fix  
**Severity:** Medium (UX Issue)  
**Status:** Fixed  
**Reviewer:** Development Team  

---

## Issue Summary

Job descriptions provided via URL were incorrectly showing "Manually entered" instead of displaying the actual source URL as a clickable link in the Analysis Results tab.

---

## Root Cause Analysis

### Backend Issue
The backend API endpoint was hardcoding job source metadata instead of accepting and persisting the actual values from the frontend:
- `source_type` was always set to `"manual"`
- `source_url` was always set to `null`

This occurred in the analyze endpoint where job description metadata was being created without reading the source information from the request payload.

### Frontend Issue
The frontend was collecting the source information in the job input state but not passing it through to the API service layer, so even if the backend accepted it, the values wouldn't have been sent.

---

## Solution Implemented

### Backend Changes (2 files)

**1. `backend/app/models/requests.py`**
- Added `source_type` field to AnalyzeRequest model
  - Type: Optional[Literal["manual", "linkedin_url"]]
  - Default: "manual"
- Added `source_url` field to AnalyzeRequest model
  - Type: Optional[str]
  - Validation: max_length=500
  - Default: None

**2. `backend/app/main.py`**
- Updated `/api/v1/analyze` endpoint to use source fields from request:
  ```python
  source_type=request.source_type,  # instead of hardcoded "manual"
  source_url=request.source_url     # instead of hardcoded None
  ```
- These values are now properly passed to the job creation and included in the analysis response

### Frontend Changes (3 files)

**1. `frontend/src/types/api.ts`**
- Added `source_type` and `source_url` fields to AnalyzeRequest interface
- Ensures TypeScript type safety for the API contract

**2. `frontend/src/services/analysisService.ts`**
- Updated AnalysisInput interface to include `sourceType` and `sourceUrl`
- Modified API request payload construction to include these fields

**3. `frontend/src/components/upload/AnalyzeButton.tsx`**
- Updated to pass `sourceType` and `sourceUrl` from Zustand store to the analysis service
- Values flow through: User input → Store → Service → API

---

## API Changes

### Request Schema Update
```typescript
// POST /api/v1/analyze
{
  cv_markdown: string;
  job_description: string;
  source_type?: "manual" | "linkedin_url";  // NEW (optional, defaults to "manual")
  source_url?: string;                       // NEW (optional, max 500 chars)
}
```

### Response Schema
No changes to response structure. The `source_type` and `source_url` fields were already part of the response schema; they just weren't being populated correctly.

---

## User-Facing Impact

### Before Fix
When a user provided a job description via LinkedIn URL:
- Source displayed as: "**Manually entered**"
- No clickable link to the original job posting
- Inconsistent with user's actual input method

### After Fix
When a user provides a job description via LinkedIn URL:
- Source displays as: "**From LinkedIn: [clickable URL]**"
- Users can click to return to the original job posting
- Accurate representation of the source

For manually entered job descriptions:
- Source continues to display as: "**Manually entered**"
- No functional change for this use case

---

## Testing Performed

### Manual Testing
- ✅ Job from LinkedIn URL: Correctly shows "From LinkedIn: [URL]" with clickable link
- ✅ Manually entered job: Correctly shows "Manually entered"
- ✅ Historical analyses: Previous analyses continue to work (backward compatible)
- ✅ Tab navigation: Source information displays correctly in Job Description tab

### Regression Testing
- ✅ Analysis workflow: Complete end-to-end analysis works as expected
- ✅ API backward compatibility: Requests without source fields use defaults
- ✅ Frontend state management: Store correctly maintains source information

---

## Related Specifications Updated

1. **`specs/features/frontend-ag-ui.md`**
   - Section FR-FE6.3: Job Description Tab
   - Added bug fix note documenting the issue and resolution

2. **`specs/features/data-persistence.md`**
   - Section FR-DP2.1: Store Job Description on Analysis
   - Added implementation note about the source fields

---

## Backward Compatibility

### API Compatibility
- **Backward compatible:** The new fields are optional with sensible defaults
- Existing API clients that don't send these fields will continue to work
- Default behavior: `source_type: "manual"`, `source_url: null`

### Data Compatibility
- Historical analyses in the database may have `null` or missing source fields
- Frontend gracefully handles missing values by defaulting to "Manually entered"
- No data migration required

---

## Future Considerations

### Potential Enhancements
1. **Auto-detect URLs in manual input:** If user pastes a URL in the manual text area, automatically set source_type to the appropriate value
2. **Source validation:** Validate that LinkedIn URLs match expected patterns
3. **Additional sources:** Support for other job boards (Indeed, Glassdoor, etc.)
4. **Source metadata:** Capture additional information like job posting date, company name from URL

### Technical Debt
None introduced by this fix. The implementation follows existing patterns and maintains consistency with the codebase.

---

## Approval

**Status:** ✅ **APPROVED AND DEPLOYED**

**Reviewed by:** Development Team  
**Deployment Date:** January 1, 2026  
**Environment:** Production  

---

## References

- Related PR: [Link to pull request if applicable]
- Issue Tracker: [Link to issue if tracked]
- User Report: Job source URL not displaying correctly in analysis results

---

**End of Review**
