# Feature Requirements Document: Data Persistence with Azure Cosmos DB

**Version:** 1.0  
**Last Updated:** January 1, 2026  
**Status:** Draft  
**Phase:** Phase 2 - Data Persistence & Storage  
**Owner:** Product Team  
**Related Documents:** [PRD](../prd.md), [ADR-004](../adr/ADR-004-no-database-v1-future-storage-design.md), [Backend README](../../backend/README.md)

---

## Table of Contents
1. [Feature Overview](#feature-overview)
2. [Business Goals](#business-goals)
3. [User Stories](#user-stories)
4. [Functional Requirements](#functional-requirements)
5. [Data Model](#data-model)
6. [Session Management](#session-management)
7. [Success Metrics](#success-metrics)
8. [Acceptance Criteria](#acceptance-criteria)
9. [Out of Scope](#out-of-scope)

---

## Feature Overview

### Purpose
Introduce persistent data storage using Azure Cosmos DB to enable CV Checker users to:
- **Save and retrieve** uploaded CVs and job descriptions
- **Access historical analyses** without re-processing
- **Track CV improvements** over time by comparing analysis scores
- **Build a personal repository** of job applications and match scores

### Goals
- Store CVs, job descriptions, and analysis results with userId-based partitioning
- Enable seamless local development using Cosmos DB Linux Emulator (Docker Compose)
- Support production deployment with Azure Cosmos DB via connection string configuration
- Provide analysis history retrieval with sorting and filtering capabilities
- Maintain data privacy through session-based user identification (no authentication yet)

### Key Value Propositions
- **Continuity:** Users don't lose work when refreshing the page or returning later
- **Insights:** Historical data reveals which CV changes improve match scores
- **Efficiency:** Re-analyze same CV against multiple jobs without re-uploading
- **Foundation:** Enable future features like progress tracking, data export, multi-device sync

### Technology Foundation
- **Database:** Azure Cosmos DB (NoSQL, serverless tier recommended)
- **Local Development:** Cosmos DB Linux Emulator via Docker Compose
- **Partitioning Strategy:** Single container with `userId` as partition key
- **Data Model:** Three entity types: CVs, Jobs, Analysis Results (differentiated by `type` field)
- **Deployment:** Environment-based connection string (local emulator vs Azure)

---

## Business Goals

### Primary Goals

**1. Retain Users Through Data Persistence**
- **Metric:** 50% of users who complete one analysis return within 7 days to perform another
- **Rationale:** Persistent data reduces friction for returning users, increasing engagement

**2. Enable Iterative CV Improvement**
- **Metric:** 40% of users analyze the same CV against 3+ different jobs
- **Rationale:** Users can test CV effectiveness across various roles without redundant uploads

**3. Provide Historical Context**
- **Metric:** 30% of users view past analysis results at least once
- **Rationale:** Historical data helps users understand what changes improved scores

**4. Simplify Development & Deployment**
- **Metric:** Local development setup completes in <5 minutes with single command
- **Rationale:** Docker Compose + emulator removes Azure dependency barrier for developers

### Secondary Goals

**5. Lay Foundation for Future Features**
- Analysis comparison (side-by-side scores)
- Progress dashboards (score trends over time)
- Data export (download all analyses as JSON/PDF)
- Multi-device sync (requires authentication in Phase 3)

**6. Maintain Privacy & Security**
- Session-based user isolation (no cross-user data leakage)
- Local storage of userId in browser (no server-side sessions)
- Clear data deletion path ("Clear My Data" button)

---

## User Stories

### Primary Persona: Sarah - Active Job Seeker

#### User Story 1: Returning User - No Re-Upload Required
**As** Sarah, a job seeker who previously used CV Checker,  
**I want to** access my previously uploaded CV without re-uploading it,  
**So that** I can quickly analyze it against new job postings.

**Acceptance Criteria:**
- On return visit, Sarah's session ID (stored in localStorage) is recognized
- Backend retrieves Sarah's CV from Cosmos DB by userId
- Frontend displays list of stored CVs (if multiple uploaded)
- Sarah selects existing CV or uploads a new version
- Analysis proceeds immediately without redundant file upload

**Priority:** P0 (Must Have - Phase 2)

---

#### User Story 2: Analyze Same CV Against Multiple Jobs
**As** Sarah,  
**I want to** store multiple job descriptions I've found,  
**So that** I can analyze my CV against 5-10 target roles and compare match scores.

**Acceptance Criteria:**
- Sarah pastes first job description → analysis saved with unique job ID
- Sarah pastes second job description → new analysis created with new job ID
- Sarah can view "Analysis History" showing all past analyses
- Each entry displays: job title (if extracted), overall score, analysis date
- Sarah can re-open any past analysis to review recommendations

**Priority:** P0 (Must Have - Phase 2)

---

#### User Story 3: Track CV Improvement Over Time
**As** Sarah,  
**I want to** see how my CV score changed after implementing recommendations,  
**So that** I can validate that my edits improved my match quality.

**Acceptance Criteria:**
- Sarah uploads CV v1 → analyzes against Job A → score 62 (Fair Match)
- Sarah implements high-priority recommendations
- Sarah uploads CV v2 → analyzes against same Job A → score 78 (Good Match)
- Analysis history shows both results with timestamps
- Sarah sees visual indicator that score improved (+16 points)

**Priority:** P1 (Should Have - Phase 2/3)

---

#### User Story 4: Clear My Data for Privacy
**As** Sarah,  
**I want to** delete all my stored CVs and analyses,  
**So that** I can ensure my data isn't accessible if I use a shared computer.

**Acceptance Criteria:**
- Frontend provides "Clear My Data" button in settings/profile area
- Clicking triggers confirmation dialog: "This will permanently delete all your CVs, jobs, and analyses. Continue?"
- Upon confirmation, frontend deletes userId from localStorage
- Backend API endpoint deletes all documents where `userId` matches session ID
- Success message confirms deletion
- Next analysis creates new userId (fresh session)

**Priority:** P1 (Should Have - Phase 2)

---

### Secondary Persona: Michael - Career Coach

#### User Story 5: Manage Multiple Client CVs
**As** Michael, a career coach,  
**I want to** store CVs from multiple clients and track their progress,  
**So that** I can provide data-driven coaching without manual record-keeping.

**Acceptance Criteria:**
- Michael uploads Client A's CV → stores with metadata (filename: "client_a_cv_v1.md")
- Michael uploads Client B's CV → stores separately
- Michael can list all stored CVs and select which to analyze
- Each analysis associates with correct CV ID
- Michael reviews history filtered by CV (all analyses for Client A)

**Priority:** P2 (Nice to Have - Phase 3 with multi-user support)

---

## Functional Requirements

### FR-DP1: CV Persistence

#### FR-DP1.1: Store CV on Analysis
**Description:** Automatically save CV content when user triggers analysis.

**Requirements:**
- **Trigger:** User uploads CV and clicks "Analyze Match"
- **Backend Action:** 
  - Extract CV content from request payload
  - Generate unique CV ID (UUID v4)
  - Create CV document in Cosmos DB container
  - Associate with userId from request header or payload
- **Document Fields:**
  ```json
  {
    "id": "cv-{uuid}",
    "type": "cv",
    "userId": "user-{uuid}",
    "content": "# John Doe\n\n## Experience...",
    "filename": "john_doe_resume.md",
    "fileSize": 2048,
    "uploadedAt": "2026-01-01T10:30:00Z",
    "lastModified": "2026-01-01T10:30:00Z"
  }
  ```
  **Note:** Partition key path is `/userId`, and the field value is the actual UUID (e.g., `"user-abc123def456"`). This is NOT a static string like `"cv"` but the specific user's session ID.
- **Response:** Include `cvId` in analysis response for future reference

**Priority:** P0 (Must Have)

---

#### FR-DP1.2: Retrieve Stored CVs
**Description:** Fetch list of user's previously uploaded CVs.

**Requirements:**
- **API Endpoint:** `GET /api/v1/cvs?userId={userId}`
- **Query Parameters:**
  - `userId` (required): Session user ID from frontend
  - `limit` (optional, default 10): Number of results to return
  - `offset` (optional, default 0): Pagination offset
- **Response:**
  ```json
  {
    "total": 3,
    "cvs": [
      {
        "id": "cv-abc123",
        "filename": "senior_engineer_cv.md",
        "uploadedAt": "2026-01-01T10:30:00Z",
        "fileSize": 2048
      }
    ]
  }
  ```
- **Sorting:** Default sort by `uploadedAt` descending (newest first)
- **Data Isolation:** Only return CVs where `userId` matches partition key

**Priority:** P1 (Should Have - Phase 2)

---

#### FR-DP1.3: Retrieve Single CV Content
**Description:** Fetch full content of a specific CV by ID.

**Requirements:**
- **API Endpoint:** `GET /api/v1/cvs/{cvId}?userId={userId}`
- **Path Parameters:** `cvId` (CV document ID)
- **Query Parameters:** `userId` (for partition key routing and authorization)
- **Response:**
  ```json
  {
    "id": "cv-abc123",
    "filename": "senior_engineer_cv.md",
    "content": "# John Doe\n\n## Experience...",
    "uploadedAt": "2026-01-01T10:30:00Z",
    "fileSize": 2048
  }
  ```
- **Authorization:** Return 404 if `userId` doesn't match CV's `userId` (prevent cross-user access)

**Priority:** P1 (Should Have - Phase 2)

---

#### FR-DP1.4: Delete CV
**Description:** Allow users to delete specific CV.

**Requirements:**
- **API Endpoint:** `DELETE /api/v1/cvs/{cvId}?userId={userId}`
- **Authorization:** Verify `userId` matches CV's `userId` before deletion
- **Cascade Behavior:** 
  - Option 1 (Phase 2): Leave orphaned analyses (cvId reference remains but CV deleted)
  - Option 2 (Phase 3): Delete all analyses associated with this cvId
- **Response:** 204 No Content on success, 404 if not found

**Priority:** P2 (Nice to Have - Phase 2/3)

---

### FR-DP2: Job Description Persistence

#### FR-DP2.1: Store Job Description on Analysis
**Description:** Save job description when user triggers analysis.

**Requirements:**
- **Trigger:** User submits job description (manual or LinkedIn URL) and clicks "Analyze Match"
- **Backend Action:**
  - Extract job description from request payload
  - Generate unique job ID (UUID v4)
  - Create job document in Cosmos DB
  - Associate with userId
- **Document Fields:**
  ```json
  {
    "id": "job-{uuid}",
    "type": "job",
    "userId": "user-{uuid}",
    "content": "We are seeking a Senior Software Engineer...",
    "sourceType": "manual" | "linkedin_url",
    "sourceUrl": "https://linkedin.com/jobs/view/123" (if applicable),
    "characterCount": 1543,
    "submittedAt": "2026-01-01T10:32:00Z",
    "extractedTitle": "Senior Software Engineer" (if parsed)
  }
  ```
  **Note:** Partition key path is `/userId`, with the field value being the user's session UUID (e.g., `"user-xyz789abc123"`), not the static string `"job"`.
- **Response:** Include `jobId` in analysis response

**Implementation Note (January 1, 2026):**
- Backend AnalyzeRequest model includes optional `source_type` (defaults to "manual") and `source_url` (optional, max 500 chars)
- Frontend properly passes these values from the job input state to the API
- This ensures job source information is correctly persisted and displayed in analysis results

**Priority:** P0 (Must Have)

---

#### FR-DP2.2: Retrieve Stored Jobs
**Description:** Fetch list of user's previously submitted job descriptions.

**Requirements:**
- **API Endpoint:** `GET /api/v1/jobs?userId={userId}`
- **Query Parameters:**
  - `userId` (required)
  - `limit` (optional, default 10)
  - `offset` (optional, default 0)
  - `sourceType` (optional filter: "manual" or "linkedin_url")
- **Response:**
  ```json
  {
    "total": 15,
    "jobs": [
      {
        "id": "job-xyz789",
        "extractedTitle": "Senior Python Developer",
        "sourceType": "linkedin_url",
        "submittedAt": "2026-01-01T10:32:00Z",
        "characterCount": 1543
      }
    ]
  }
  ```
- **Sorting:** Default sort by `submittedAt` descending

**Priority:** P1 (Should Have - Phase 2)

---

#### FR-DP2.3: Retrieve Single Job Description
**Description:** Fetch full content of a specific job by ID.

**Requirements:**
- **API Endpoint:** `GET /api/v1/jobs/{jobId}?userId={userId}`
- **Response:**
  ```json
  {
    "id": "job-xyz789",
    "content": "We are seeking a Senior Software Engineer...",
    "sourceType": "linkedin_url",
    "sourceUrl": "https://linkedin.com/jobs/view/123",
    "submittedAt": "2026-01-01T10:32:00Z"
  }
  ```
- **Authorization:** Return 404 if `userId` mismatch

**Priority:** P1 (Should Have - Phase 2)

---

### FR-DP3: Analysis Results Persistence

#### FR-DP3.1: Store Analysis Results
**Description:** Persist full analysis output for historical access.

**Requirements:**
- **Trigger:** Analysis orchestration completes successfully
- **Backend Action:**
  - Generate unique analysis ID (UUID v4)
  - Create analysis document in Cosmos DB
  - Include references to cvId and jobId
  - Associate with userId
- **Document Fields:**
  ```json
  {
    "id": "analysis-{uuid}",
    "type": "analysis",
    "userId": "user-{uuid}",
    "cvId": "cv-abc123",
    "jobId": "job-xyz789",
    "overallScore": 75,
    "subscores": {
      "skillsMatch": 80,
      "experienceMatch": 70,
      "keywordMatch": 75,
      "educationMatch": 85
    },
    "strengths": [
      "Strong Python and FastAPI skills",
      "Relevant API development experience"
    ],
    "gaps": [
      "Missing PostgreSQL experience",
      "Limited leadership mentions"
    ],
    "recommendations": [
      "Add PostgreSQL to technical skills section",
      "Emphasize leadership experience in project descriptions"
    ],
    "analyzedAt": "2026-01-01T10:35:00Z",
    "processingDuration": 23.5
  }
  ```
- **Indexing:** Ensure `userId`, `cvId`, `jobId`, `analyzedAt`, `overallScore` are indexed for efficient queries

**Priority:** P0 (Must Have)

---

#### FR-DP3.2: Retrieve Analysis History
**Description:** Fetch list of user's past analyses with sorting and filtering.

**Requirements:**
- **API Endpoint:** `GET /api/v1/analyses?userId={userId}&sortBy={field}&order={asc|desc}&limit={n}&offset={n}`
- **Query Parameters:**
  - `userId` (required)
  - `sortBy` (optional, default "analyzedAt"): "analyzedAt" | "overallScore"
  - `order` (optional, default "desc"): "asc" | "desc"
  - `limit` (optional, default 10, max 50)
  - `offset` (optional, default 0)
  - `cvId` (optional filter): Return only analyses for specific CV
  - `jobId` (optional filter): Return only analyses for specific job
  - `minScore` / `maxScore` (optional filter): Score range filtering
- **Response:**
  ```json
  {
    "total": 23,
    "analyses": [
      {
        "id": "analysis-def456",
        "cvId": "cv-abc123",
        "jobId": "job-xyz789",
        "cvFilename": "senior_engineer_cv.md",
        "jobTitle": "Senior Python Developer",
        "overallScore": 75,
        "analyzedAt": "2026-01-01T10:35:00Z"
      }
    ]
  }
  ```
- **Performance:** Use Cosmos DB continuation tokens for pagination (more efficient than offset-based)

**Priority:** P0 (Must Have)

---

#### FR-DP3.3: Retrieve Single Analysis Result
**Description:** Fetch full details of a specific past analysis.

**Requirements:**
- **API Endpoint:** `GET /api/v1/analyses/{analysisId}?userId={userId}`
- **Response:** Complete analysis document including:
  - Overall score and subscores
  - Strengths and gaps
  - Full recommendations list
  - Analysis timestamp
  - References to CV and job (IDs and titles/filenames)
- **Authorization:** Return 404 if `userId` mismatch
- **Use Case:** User clicks on history entry → frontend displays full analysis results

**Priority:** P0 (Must Have)

---

### FR-DP7: REST API Endpoint Specifications

#### FR-DP7.1: API Endpoint Summary
**Description:** Complete REST API endpoint definitions with request/response schemas.

**Endpoints:**

**1. Analyze CV (with persistence)**
```
POST /api/v1/analyze
Headers:
  X-User-Id: user-{uuid}
  Content-Type: application/json

Request Body:
{
  "cv_markdown": string (required, max 100KB),
  "job_description": string (required, max 50KB),
  "source_type": "manual" | "linkedin_url" (optional, default "manual"),
  "source_url": string (optional, only if source_type="linkedin_url")
}

Response (200 OK):
{
  "cvId": "cv-abc123",
  "jobId": "job-xyz789",
  "analysisId": "analysis-def456",
  "overallScore": 75,
  "subscores": { "skillsMatch": 80, "experienceMatch": 70, ... },
  "strengths": ["..."],
  "gaps": ["..."],
  "recommendations": ["..."],
  "analyzedAt": "2026-01-01T10:35:00Z"
}

Errors:
  400 Bad Request: Invalid input (missing fields, size limits exceeded)
  401 Unauthorized: Missing or invalid X-User-Id header
  503 Service Unavailable: Database connection failed
  500 Internal Server Error: Analysis processing failed
```

**2. List User CVs**
```
GET /api/v1/cvs?userId={userId}&limit={n}&offset={n}
Headers:
  X-User-Id: user-{uuid}

Query Parameters:
  userId: string (required, must match X-User-Id header)
  limit: integer (optional, default 10, max 50)
  offset: integer (optional, default 0)

Response (200 OK):
{
  "total": 3,
  "limit": 10,
  "offset": 0,
  "cvs": [
    {
      "id": "cv-abc123",
      "filename": "senior_engineer_cv.md",
      "uploadedAt": "2026-01-01T10:30:00Z",
      "fileSize": 2048
    }
  ]
}

Errors:
  401 Unauthorized: userId parameter doesn't match X-User-Id header
  503 Service Unavailable: Database unavailable
```

**3. Get Single CV**
```
GET /api/v1/cvs/{cvId}?userId={userId}
Headers:
  X-User-Id: user-{uuid}

Path Parameters:
  cvId: string (CV document ID)

Query Parameters:
  userId: string (required, must match X-User-Id header)

Response (200 OK):
{
  "id": "cv-abc123",
  "filename": "senior_engineer_cv.md",
  "content": "# John Doe\n\n## Experience...",
  "uploadedAt": "2026-01-01T10:30:00Z",
  "fileSize": 2048
}

Errors:
  404 Not Found: CV doesn't exist or userId mismatch
  401 Unauthorized: userId parameter doesn't match X-User-Id header
  503 Service Unavailable: Database unavailable
```

**4. List User Jobs**
```
GET /api/v1/jobs?userId={userId}&limit={n}&offset={n}&sourceType={type}
Headers:
  X-User-Id: user-{uuid}

Query Parameters:
  userId: string (required)
  limit: integer (optional, default 10, max 50)
  offset: integer (optional, default 0)
  sourceType: string (optional, "manual" | "linkedin_url")

Response (200 OK):
{
  "total": 15,
  "limit": 10,
  "offset": 0,
  "jobs": [
    {
      "id": "job-xyz789",
      "extractedTitle": "Senior Python Developer",
      "sourceType": "linkedin_url",
      "submittedAt": "2026-01-01T10:32:00Z",
      "characterCount": 1543
    }
  ]
}
```

**5. Get Single Job**
```
GET /api/v1/jobs/{jobId}?userId={userId}
Headers:
  X-User-Id: user-{uuid}

Response (200 OK):
{
  "id": "job-xyz789",
  "content": "We are seeking...",
  "sourceType": "linkedin_url",
  "sourceUrl": "https://linkedin.com/jobs/view/123",
  "submittedAt": "2026-01-01T10:32:00Z",
  "extractedTitle": "Senior Python Developer"
}
```

**6. List Analysis History**
```
GET /api/v1/analyses?userId={userId}&sortBy={field}&order={asc|desc}&limit={n}&offset={n}&cvId={id}&jobId={id}&minScore={n}&maxScore={n}
Headers:
  X-User-Id: user-{uuid}

Query Parameters:
  userId: string (required)
  sortBy: string (optional, default "analyzedAt", allowed: "analyzedAt", "overallScore")
  order: string (optional, default "desc", allowed: "asc", "desc")
  limit: integer (optional, default 10, max 50)
  offset: integer (optional, default 0)
  cvId: string (optional, filter by CV)
  jobId: string (optional, filter by job)
  minScore: integer (optional, 0-100)
  maxScore: integer (optional, 0-100)

Response (200 OK):
{
  "total": 23,
  "limit": 10,
  "offset": 0,
  "analyses": [
    {
      "id": "analysis-def456",
      "cvId": "cv-abc123",
      "jobId": "job-xyz789",
      "cvFilename": "senior_engineer_cv.md",
      "jobTitle": "Senior Python Developer",
      "overallScore": 75,
      "analyzedAt": "2026-01-01T10:35:00Z"
    }
  ]
}
```

**7. Get Single Analysis**
```
GET /api/v1/analyses/{analysisId}?userId={userId}
Headers:
  X-User-Id: user-{uuid}

Response (200 OK):
{
  "id": "analysis-def456",
  "cvId": "cv-abc123",
  "jobId": "job-xyz789",
  "overallScore": 75,
  "subscores": { ... },
  "strengths": [...],
  "gaps": [...],
  "recommendations": [...],
  "analyzedAt": "2026-01-01T10:35:00Z",
  "processingDuration": 23.5
}
```

**8. Delete CV**
```
DELETE /api/v1/cvs/{cvId}?userId={userId}
Headers:
  X-User-Id: user-{uuid}

Response:
  204 No Content: Successfully deleted
  404 Not Found: CV doesn't exist or userId mismatch
```

**9. Clear All User Data**
```
DELETE /api/v1/users/{userId}/data
Headers:
  X-User-Id: user-{uuid}

Response (200 OK):
{
  "deletedCVs": 3,
  "deletedJobs": 15,
  "deletedAnalyses": 23,
  "message": "All user data deleted successfully"
}

Errors:
  401 Unauthorized: userId path parameter doesn't match X-User-Id header
```

**10. Health Check**
```
GET /api/v1/health

Response (200 OK):
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-01-01T10:00:00Z"
}

Response (503 Service Unavailable):
{
  "status": "unhealthy",
  "database": "disconnected",
  "timestamp": "2026-01-01T10:00:00Z"
}
```

**Priority:** P0 (Must Have)

**Related ADR:** [ADR-008](../adr/ADR-008-cosmos-db-data-persistence.md)

---

### FR-DP8: Error Handling for Database Unavailability

#### FR-DP8.1: Database Connection Failure Handling
**Description:** Gracefully handle scenarios where Cosmos DB is unavailable.

**Requirements:**
- **Detection:** Backend detects database connection failure on startup or during operations
- **Startup Behavior:**
  - If database unavailable during backend startup → log error, set health check to "disconnected"
  - Backend continues running (doesn't crash) but returns 503 for data operations
  - Health check endpoint always responds (200 or 503) showing database status
- **Runtime Behavior:**
  - Database operations that fail return 503 Service Unavailable with clear error message
  - Error response:
    ```json
    {
      "error": "Service Unavailable",
      "message": "Database connection failed. Please try again later.",
      "retryAfter": 30
    }
    ```
  - Frontend displays user-friendly message: "Our service is temporarily unavailable. Your data is safe. Please try again in a moment."
- **Retry Logic:**
  - Backend implements exponential backoff for connection retries (1s, 2s, 4s, 8s, max 30s)
  - After 3 failed attempts, backend waits for manual intervention or health check to restore
- **Logging:**
  - Log database connection errors with full exception details (for debugging)
  - Include Cosmos DB endpoint, error code, and timestamp
  - Alert operations team if database unavailable for >5 minutes (future monitoring integration)

**Local Development Scenario:**
- Developer forgets to run `docker-compose up` → emulator not running
- Backend startup logs: `ERROR: Cosmos DB connection failed. Is emulator running? Run 'docker-compose up -d'`
- Health check: `{"database": "disconnected", "message": "Emulator not running"}`
- API requests: Return 503 with helpful error message

**Production Scenario:**
- Azure Cosmos DB region outage or network partition
- Backend logs error, continues serving health check endpoint
- Frontend shows maintenance banner: "Data operations temporarily unavailable"
- Analysis requests still processed in-memory (results not persisted) OR rejected with 503 (decision TBD)

**Priority:** P0 (Must Have - critical for production reliability)

**Related:** See [ADR-008](../adr/ADR-008-cosmos-db-data-persistence.md) for error handling implementation details

---

### FR-DP9: Input Validation and Security Requirements

#### FR-DP9.1: Request Input Validation
**Description:** Validate all user inputs to prevent security vulnerabilities and data corruption.

**Requirements:**

**1. User ID Validation**
- Format: `user-{uuid}` where uuid is valid UUID v4
- Header `X-User-Id` must be present and match query parameter `userId` in all endpoints
- Reject requests with mismatched or malformed user IDs (401 Unauthorized)
- Example validation regex: `^user-[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`

**2. Content Size Limits**
- CV content: Maximum 100KB (approx. 50,000 words)
- Job description: Maximum 50KB (approx. 25,000 words)
- Reject oversized content with 400 Bad Request:
  ```json
  {
    "error": "Payload Too Large",
    "message": "CV content exceeds 100KB limit",
    "maxSize": 102400
  }
  ```

**3. Required Field Validation**
- `POST /api/v1/analyze`: Require `cv_markdown`, `job_description`
- All GET endpoints with `userId` parameter: Require matching `X-User-Id` header
- Return 400 Bad Request with specific missing field name

**4. Query Parameter Validation**
- `limit`: Integer between 1 and 50 (default 10)
- `offset`: Non-negative integer (default 0)
- `sortBy`: Allowed values only ("analyzedAt", "overallScore")
- `order`: "asc" or "desc" only
- `minScore`/`maxScore`: Integer 0-100, minScore ≤ maxScore
- Invalid values return 400 Bad Request with explanation

**5. Content Sanitization**
- CV and job description content stored as-is (no HTML stripping—Markdown expected)
- No executable code allowed (validated on frontend before submission)
- Special characters in filenames: Sanitize to alphanumeric + underscore/hyphen only

**6. Rate Limiting (Future - Phase 3)**
- Not implemented in Phase 2 (no authentication)
- Placeholder for per-user rate limits (e.g., 100 analyses per day)

**Priority:** P0 (Must Have - security critical)

---

#### FR-DP9.2: Security Best Practices
**Description:** Implement security measures for data protection.

**Requirements:**

**1. Connection String Security**
- **Production:** Store Cosmos DB connection string in Azure Key Vault (see [ADR-008](../adr/ADR-008-cosmos-db-data-persistence.md))
- **Local Development:** Use emulator's default connection string (acceptable—no sensitive data)
- Never commit connection strings to Git (`.env` files in `.gitignore`)
- App Service environment variables only accessible by backend application

**2. HTTPS Enforcement**
- All API endpoints require HTTPS in production (enforced by Azure App Service)
- Cosmos DB connections use TLS 1.2+ (Azure default)
- Local development: HTTP acceptable for frontend ↔ backend, HTTPS for backend ↔ emulator

**3. Cross-Origin Resource Sharing (CORS)**
- Backend allows requests only from known frontend domain (configured in App Service)
- Local development: Allow `http://localhost:5173` (Vite dev server)
- Production: Allow `https://cv-checker.azurewebsites.net` (or custom domain)

**4. Data Isolation**
- Partition key (`userId`) enforces logical data isolation
- Backend validates `userId` in header matches query parameter (prevents cross-user access)
- Cosmos DB queries scoped to single partition (cannot query other users' data)

**5. Secrets Management**
- Use Azure Key Vault for production secrets (connection string, API keys)
- Managed Identity for Key Vault access (no credentials in code)
- See [ADR-008 Security Section](../adr/ADR-008-cosmos-db-data-persistence.md#security-best-practices) for implementation details

**6. Audit Logging (Future - Phase 3)**
- Log all data access operations (create, read, delete) with userId and timestamp
- Use Azure Monitor for audit trail (when user deleted data, etc.)
- Not implemented in Phase 2 (defer to Phase 3 with authentication)

**Priority:** P0 (Must Have - Key Vault for MVP per Dev Lead decision)

**Related ADR:** [ADR-008](../adr/ADR-008-cosmos-db-data-persistence.md) for detailed security implementation

---

### FR-DP4: Session Management

#### FR-DP4.1: Generate User ID (Frontend)
**Description:** Frontend generates and persists session-based user ID.

**Requirements:**
- **Trigger:** User's first visit to application (no userId in localStorage)
- **Frontend Action:**
  - Generate UUID v4: `crypto.randomUUID()` or equivalent
  - Prefix with "user-" for clarity: `user-{uuid}`
  - Store in localStorage: `localStorage.setItem('cv-checker-userId', userId)`
  - Include in all API requests (header: `X-User-Id` or query param)
- **Persistence:** userId remains in localStorage indefinitely (until user clears browser data)
- **Privacy Notice:** Display one-time message: "Your data is stored locally in your browser. Clearing browser data will remove your session."

**Priority:** P0 (Must Have)

---

#### FR-DP4.2: Retrieve User ID on Subsequent Visits
**Description:** Frontend reuses existing userId from localStorage.

**Requirements:**
- **Trigger:** User returns to application
- **Frontend Action:**
  - Check localStorage for `cv-checker-userId`
  - If exists: Use existing userId for all API requests
  - If missing: Generate new userId (treat as first visit)
- **Backend:** Validate userId format (UUID v4 pattern)

**Priority:** P0 (Must Have)

---

#### FR-DP4.3: Clear User Data
**Description:** Allow user to delete all stored data and reset session.

**Requirements:**
- **Frontend UI:** "Clear My Data" button in settings or help section
- **Confirmation Dialog:** 
  - Title: "Delete All Your Data?"
  - Message: "This will permanently delete all your CVs, job descriptions, and analyses. This action cannot be undone."
  - Actions: "Cancel" (default) | "Delete Everything" (destructive, red)
- **Backend Endpoint:** `DELETE /api/v1/users/{userId}/data`
- **Backend Action:**
  - Query all documents where `userId` matches
  - Delete CVs, jobs, and analyses in batch
  - Return count of deleted items
- **Frontend Action:**
  - Remove `cv-checker-userId` from localStorage
  - Generate new userId for next session
  - Redirect to home page with confirmation: "All your data has been deleted."

**Priority:** P1 (Should Have - Phase 2)

---

### FR-DP5: Local Development with Cosmos DB Emulator

#### FR-DP5.1: Docker Compose Setup
**Description:** Provide single-command setup for local development with Cosmos DB emulator.

**Requirements:**
- **Docker Compose File:** `docker-compose.yml` in project root
- **Services:**
  - `cosmosdb`: Cosmos DB Linux Emulator (latest stable image)
    - Port: 8081 (HTTPS endpoint)
    - Port: 10251-10254 (other endpoints)
  - `backend`: FastAPI application
    - Depends on `cosmosdb` service
    - Environment variable: `COSMOS_CONNECTION_STRING=https://cosmosdb:8081/...`
- **Startup Command:** `docker-compose up -d`
- **Verification:**
  - Cosmos DB emulator UI accessible at `https://localhost:8081/_explorer/index.html`
  - Backend health check succeeds: `curl http://localhost:8000/api/v1/health`
- **Documentation:** README with step-by-step setup instructions

**Priority:** P0 (Must Have)

---

#### FR-DP5.2: Emulator Connection String
**Description:** Configure backend to use emulator connection string in local environment.

**Requirements:**
- **Connection String Format:**
  ```
  AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv35VFMA6rHH9NX0x6UqOgE=;
  ```
  (Default emulator key - same for all developers)
- **Backend Configuration:**
  - Read from environment variable: `COSMOS_CONNECTION_STRING`
  - `.env.local` (git-ignored): Local development value
  - `.env.production`: Azure Cosmos DB connection string (from Azure Key Vault or environment)
- **Cosmos Client Initialization:**
  - Detect local environment (emulator uses well-known hostname "localhost")
  - Disable SSL verification for emulator (self-signed cert)
  - Production: Enforce SSL verification

**Priority:** P0 (Must Have)

---

#### FR-DP5.3: Database Initialization
**Description:** Automatically create database and container on first run.

**Requirements:**
- **Initialization Script:** Backend startup checks if database/container exists
- **If Not Exists:**
  - Create database: `cv-checker-db`
  - Create container: `cv-checker-data`
  - Partition key: `/userId`
  - Indexing policy: Index `type`, `userId`, `analyzedAt`, `overallScore`
- **Idempotent:** Safe to run multiple times (no errors if already exists)
- **Logging:** Log initialization steps for debugging

**Priority:** P0 (Must Have)

---

### FR-DP6: Production Deployment with Azure Cosmos DB

#### FR-DP6.1: Serverless Tier (Recommended)
**Description:** Use Azure Cosmos DB serverless tier for cost-effective MVP deployment.

**Requirements:**
- **Tier:** Serverless (pay-per-request, no minimum RU/s provisioning)
- **Region:** Same as backend (e.g., East US) to minimize latency
- **Consistency:** Session consistency (default, balances performance and cost)
- **Connection String Source:** 
  - Azure Key Vault secret (recommended)
  - OR App Service environment variable (less secure but simpler for MVP)
- **Monitoring:** Enable Azure Monitor metrics (request units, latency, throttling)

**Priority:** P0 (Must Have)

---

#### FR-DP6.2: Seamless Environment Swap
**Description:** Switch from local emulator to Azure Cosmos DB via configuration only.

**Requirements:**
- **No Code Changes:** Backend reads `COSMOS_CONNECTION_STRING` environment variable
- **Local Development:** `COSMOS_CONNECTION_STRING=AccountEndpoint=https://localhost:8081/;...`
- **Production:** `COSMOS_CONNECTION_STRING=AccountEndpoint=https://<account-name>.documents.azure.com:443/;AccountKey=...;`
- **Deployment:**
  - CI/CD pipeline sets production connection string in App Service environment variables
  - Backend restarts → connects to Azure Cosmos DB automatically
- **Validation:** Health check endpoint verifies Cosmos DB connectivity on startup

**Priority:** P0 (Must Have)

---

## Data Model

### Container Structure

**Single Container Approach:**
- **Container Name:** `cv-checker-data`
- **Partition Key:** `/userId`
- **Entity Differentiation:** `type` field (`"cv"`, `"job"`, `"analysis"`)

**Rationale:**
- Simplifies queries (all user data in same partition)
- Reduces Cosmos DB costs (single container = fewer RU charges)
- Enables future expansion (add more entity types without schema migration)

---

### Document Schemas

#### CV Document
```json
{
  "id": "cv-{uuid}",
  "type": "cv",
  "userId": "user-{uuid}",
  "content": "# John Doe\n\n## Professional Summary\n...",
  "filename": "john_doe_resume.md",
  "fileSize": 2048,
  "uploadedAt": "2026-01-01T10:30:00Z",
  "lastModified": "2026-01-01T10:30:00Z",
  "_ts": 1735729800
}
```

**Fields:**
- `id` (string, required): Unique identifier with "cv-" prefix
- `type` (string, required): Always "cv" (discriminator)
- `userId` (string, required): Partition key, user session ID
- `content` (string, required): Full CV text in Markdown format
- `filename` (string, optional): Original filename from upload
- `fileSize` (number, required): File size in bytes
- `uploadedAt` (ISO 8601, required): Upload timestamp
- `lastModified` (ISO 8601, optional): Last edit timestamp (future feature)
- `_ts` (number, automatic): Cosmos DB system timestamp (seconds since epoch)

---

#### Job Document
```json
{
  "id": "job-{uuid}",
  "type": "job",
  "userId": "user-{uuid}",
  "content": "We are seeking a Senior Software Engineer with 5+ years...",
  "sourceType": "manual",
  "sourceUrl": null,
  "characterCount": 1543,
  "submittedAt": "2026-01-01T10:32:00Z",
  "extractedTitle": "Senior Software Engineer",
  "_ts": 1735729920
}
```

**Fields:**
- `id` (string, required): Unique identifier with "job-" prefix
- `type` (string, required): Always "job"
- `userId` (string, required): Partition key
- `content` (string, required): Full job description text
- `sourceType` (string, required): "manual" or "linkedin_url"
- `sourceUrl` (string, optional): LinkedIn URL if applicable
- `characterCount` (number, required): Length of job description
- `submittedAt` (ISO 8601, required): Submission timestamp
- `extractedTitle` (string, optional): Job title extracted by Job Parser Agent
- `_ts` (number, automatic): Cosmos DB system timestamp

---

#### Analysis Document
```json
{
  "id": "analysis-{uuid}",
  "type": "analysis",
  "userId": "user-{uuid}",
  "cvId": "cv-abc123",
  "jobId": "job-xyz789",
  "overallScore": 75,
  "subscores": {
    "skillsMatch": 80,
    "experienceMatch": 70,
    "keywordMatch": 75,
    "educationMatch": 85
  },
  "strengths": [
    "Strong Python and FastAPI skills match job requirements",
    "Relevant API development experience",
    "AWS certification aligns with preferred skills"
  ],
  "gaps": [
    "Missing PostgreSQL experience",
    "Limited leadership or mentoring mentions",
    "Architecture terminology not prominent"
  ],
  "recommendations": [
    "Add PostgreSQL to technical skills section if you have experience",
    "Expand on any leadership responsibilities in past roles",
    "Incorporate keywords like 'architecture' and 'system design' in experience descriptions"
  ],
  "analyzedAt": "2026-01-01T10:35:00Z",
  "processingDuration": 23.5,
  "_ts": 1735730100
}
```

**Fields:**
- `id` (string, required): Unique identifier with "analysis-" prefix
- `type` (string, required): Always "analysis"
- `userId` (string, required): Partition key
- `cvId` (string, required): Reference to CV document
- `jobId` (string, required): Reference to Job document
- `overallScore` (number, required): 0-100 match score
- `subscores` (object, required): Breakdown by category
  - `skillsMatch` (number, 0-100)
  - `experienceMatch` (number, 0-100)
  - `keywordMatch` (number, 0-100)
  - `educationMatch` (number, 0-100)
- `strengths` (array of strings, required): Top 3-5 positive findings
- `gaps` (array of strings, required): Top 3-5 missing elements
- `recommendations` (array of strings, required): 5-10 actionable suggestions
- `analyzedAt` (ISO 8601, required): Analysis completion timestamp
- `processingDuration` (number, optional): Time in seconds to complete analysis
- `_ts` (number, automatic): Cosmos DB system timestamp

---

### Indexing Policy

**Automatic Indexing:**
- All fields indexed by default (Cosmos DB default behavior)
- Optimized for common queries:
  - `SELECT * FROM c WHERE c.userId = 'user-123' AND c.type = 'analysis' ORDER BY c.analyzedAt DESC`
  - `SELECT * FROM c WHERE c.userId = 'user-123' AND c.type = 'cv'`

**Custom Indexing (Optional Optimization):**
```json
{
  "indexingPolicy": {
    "automatic": true,
    "includedPaths": [
      { "path": "/userId/*" },
      { "path": "/type/*" },
      { "path": "/analyzedAt/*" },
      { "path": "/overallScore/*" },
      { "path": "/cvId/*" },
      { "path": "/jobId/*" }
    ],
    "excludedPaths": [
      { "path": "/content/*" },
      { "path": "/recommendations/*" }
    ]
  }
}
```

**Rationale:**
- Include frequently queried fields (userId, type, analyzedAt, score)
- Exclude large text fields (content, recommendations) to reduce index size and RU consumption

---

## Session Management

### Frontend: User ID Generation & Storage

**Implementation:**
```typescript
// src/utils/session.ts

export function getUserId(): string {
  const storageKey = 'cv-checker-userId';
  let userId = localStorage.getItem(storageKey);
  
  if (!userId) {
    // Generate new UUID v4
    userId = `user-${crypto.randomUUID()}`;
    localStorage.setItem(storageKey, userId);
    console.log('New user session created:', userId);
  }
  
  return userId;
}

export function clearUserData(): void {
  const userId = getUserId();
  
  // Call backend to delete all user data
  fetch(`/api/v1/users/${userId}/data`, { method: 'DELETE' })
    .then(() => {
      localStorage.removeItem('cv-checker-userId');
      window.location.href = '/'; // Redirect to home
    });
}
```

**Usage in API Calls:**
```typescript
// src/api/client.ts

import { getUserId } from '@/utils/session';

export async function analyzeCV(cvMarkdown: string, jobDescription: string) {
  const userId = getUserId();
  
  const response = await fetch('/api/v1/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-User-Id': userId
    },
    body: JSON.stringify({
      cv_markdown: cvMarkdown,
      job_description: jobDescription
    })
  });
  
  return response.json();
}
```

---

### Backend: User ID Validation & Extraction

**FastAPI Dependency:**
```python
# backend/app/dependencies.py

from fastapi import Header, HTTPException

def get_user_id(x_user_id: str = Header(...)) -> str:
    """Extract and validate userId from request header."""
    if not x_user_id.startswith("user-"):
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Optional: Validate UUID format
    try:
        uuid_part = x_user_id.replace("user-", "")
        uuid.UUID(uuid_part)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    return x_user_id
```

**Usage in Endpoints:**
```python
# backend/app/main.py

from app.dependencies import get_user_id

@app.post("/api/v1/analyze")
async def analyze_cv(
    request: AnalyzeRequest,
    user_id: str = Depends(get_user_id)
):
    # Store CV with userId
    cv_id = await repository.create_cv(
        user_id=user_id,
        content=request.cv_markdown,
        filename="uploaded_cv.md"
    )
    
    # Store job with userId
    job_id = await repository.create_job(
        user_id=user_id,
        content=request.job_description,
        source_type="manual"
    )
    
    # Run analysis...
    result = await orchestrator.analyze(cv_id, job_id)
    
    # Store analysis with userId
    analysis_id = await repository.create_analysis(
        user_id=user_id,
        cv_id=cv_id,
        job_id=job_id,
        result=result
    )
    
    return result
```

---

### Privacy Considerations

**What We Store:**
- Session UUID (generated on frontend, not tied to identity)
- CV content (markdown text)
- Job descriptions (publicly posted job content)
- Analysis results (scores, recommendations)

**What We DON'T Store:**
- Email addresses
- Passwords
- IP addresses (not logged in database)
- Browser fingerprints
- User names (unless in CV content itself)

**User Control:**
- Users can delete all data via "Clear My Data" button
- Data accessible only via session UUID (no cross-user access)
- No data shared with third parties
- No data used for training ML models (analysis is stateless per request)

**Limitations (Addressed in Phase 3):**
- No GDPR "Download My Data" feature (Phase 3)
- No multi-device sync (requires authentication)
- Browser data loss = permanent loss of session access
- No email notifications or password reset (no accounts yet)

---

## Success Metrics

### Business Metrics

**1. User Retention**
- **Target:** 50% of users who complete one analysis return within 7 days
- **Measurement:** Track `userId` in analyses, count unique returning users
- **Rationale:** Data persistence should drive return visits

**2. Multi-Analysis Engagement**
- **Target:** 40% of users perform 3+ analyses within first month
- **Measurement:** Count analyses per userId in 30-day window
- **Rationale:** Persistent storage encourages testing multiple jobs

**3. History Usage**
- **Target:** 30% of users view at least one past analysis
- **Measurement:** Track API calls to `GET /api/v1/analyses/{id}`
- **Rationale:** Historical data has value if users actually access it

**4. Data Persistence Awareness**
- **Target:** 80% of users understand their data is stored (post-use survey)
- **Measurement:** User survey: "Did you know your CVs and analyses are saved for future visits?"
- **Rationale:** Users should be aware of persistence benefit

---

### Technical Metrics

**5. Database Performance**
- **Target:** 95% of queries complete in <100ms (p95 latency)
- **Measurement:** Cosmos DB metrics (Request Units consumed, latency)
- **Rationale:** Fast data retrieval improves UX

**6. Data Integrity**
- **Target:** 99.9% success rate for write operations
- **Measurement:** Monitor failed Cosmos DB inserts/updates
- **Rationale:** Data loss undermines persistence value

**7. Local Development Experience**
- **Target:** Developers set up local environment in <5 minutes
- **Measurement:** Time from `git clone` to `docker-compose up` success
- **Rationale:** Emulator should remove friction

**8. Cost Efficiency (Production)**
- **Target:** Cosmos DB costs <$20/month for 1,000 analyses
- **Measurement:** Azure Cost Management (Cosmos DB resource)
- **Rationale:** Serverless tier should be cost-effective at MVP scale

---

## Acceptance Criteria

### AC-DP1: CV Persistence (Phase 2)

- [ ] User uploads CV and triggers analysis → CV stored in Cosmos DB with userId
- [ ] CV document includes: id, userId, content, filename, fileSize, uploadedAt
- [ ] Backend API endpoint `GET /api/v1/cvs?userId={userId}` returns list of user's CVs
- [ ] Backend API endpoint `GET /api/v1/cvs/{cvId}?userId={userId}` returns full CV content
- [ ] Authorization: Users can only access their own CVs (userId partition isolation)
- [ ] CV content retrieved successfully and used for re-analysis without re-upload

---

### AC-DP2: Job Description Persistence (Phase 2)

- [ ] User submits job description → stored in Cosmos DB with userId
- [ ] Job document includes: id, userId, content, sourceType, submittedAt, extractedTitle
- [ ] Backend API `GET /api/v1/jobs?userId={userId}` returns list of user's jobs
- [ ] Backend API `GET /api/v1/jobs/{jobId}?userId={userId}` returns full job content
- [ ] Jobs associated with userId (partition key)
- [ ] Job descriptions from both manual input and LinkedIn URLs stored correctly

---

### AC-DP3: Analysis History (Phase 2)

- [ ] Analysis results stored in Cosmos DB after completion
- [ ] Analysis document includes: id, userId, cvId, jobId, scores, recommendations, analyzedAt
- [ ] Backend API `GET /api/v1/analyses?userId={userId}` returns paginated list (default 10 per page)
- [ ] Results sorted by `analyzedAt` descending (newest first) by default
- [ ] Alternative sort: `GET /api/v1/analyses?userId={userId}&sortBy=overallScore&order=desc`
- [ ] Filtering: `GET /api/v1/analyses?userId={userId}&minScore=70` returns only analyses scoring ≥70
- [ ] Backend API `GET /api/v1/analyses/{analysisId}?userId={userId}` returns full analysis details
- [ ] Frontend displays analysis history with date, score, CV filename, job title

---

### AC-DP4: Session Management (Phase 2)

- [ ] Frontend generates UUID on first visit if not present in localStorage
- [ ] UserId stored in localStorage: `cv-checker-userId`
- [ ] UserId persists across page refreshes and browser restarts
- [ ] All API requests include userId in `X-User-Id` header
- [ ] Backend validates userId format (UUID v4 with "user-" prefix)
- [ ] Frontend "Clear My Data" button triggers confirmation dialog
- [ ] Backend endpoint `DELETE /api/v1/users/{userId}/data` deletes all user documents
- [ ] After deletion, localStorage cleared and new userId generated on next action

---

### AC-DP5: Local Development (Phase 2)

- [ ] `docker-compose.yml` includes Cosmos DB Linux Emulator service
- [ ] `docker-compose up -d` starts emulator and backend successfully
- [ ] Cosmos DB emulator accessible at `https://localhost:8081/_explorer/index.html`
- [ ] Backend connects to emulator using default connection string (from `.env.local`)
- [ ] Backend automatically creates database `cv-checker-db` and container `cv-checker-data` on first run
- [ ] Container partition key set to `/userId`
- [ ] Full CRUD operations (create, read, update, delete) work against emulator
- [ ] Developer can clear emulator data and restart without issues

---

### AC-DP6: Production Deployment (Phase 2)

- [ ] Azure Cosmos DB account created in same region as backend
- [ ] Serverless tier configured
- [ ] Connection string stored in Azure Key Vault (per Dev Lead decision: Key Vault for MVP)
- [ ] App Service configured to retrieve connection string from Key Vault via Managed Identity
- [ ] Backend connects to Azure Cosmos DB on startup (verified via health check endpoint)
- [ ] Database and container created in Azure (manually or via initialization script)
- [ ] Analysis workflow succeeds in production environment (end-to-end test)
- [ ] Cosmos DB metrics monitored (request units, latency, error rate)
- [ ] RU budget alert configured: Alert at 50,000 RU/month (target: <100,000 RU/month, ~$3/month)
- [ ] No code changes required between local and production environments (config-driven)

---

### AC-DP7: Comprehensive Testing Strategy (Phase 2)

**Unit Tests (Backend Repository Layer):**

- [ ] **CV Repository Tests:**
  - [ ] `test_create_cv()`: Creates CV document with correct schema (id, type, userId, content, metadata)
  - [ ] `test_get_cv_by_id()`: Retrieves CV by ID and userId (partition key)
  - [ ] `test_get_cv_not_found()`: Returns None when CV doesn't exist
  - [ ] `test_get_cv_wrong_user()`: Returns None when userId mismatch (data isolation)
  - [ ] `test_list_user_cvs()`: Returns paginated list sorted by uploadedAt desc
  - [ ] `test_list_cvs_empty()`: Returns empty list for new user
  - [ ] `test_delete_cv()`: Deletes CV successfully
  - [ ] `test_delete_cv_wrong_user()`: Fails to delete CV with userId mismatch

- [ ] **Job Repository Tests:**
  - [ ] `test_create_job()`: Creates job with manual source type
  - [ ] `test_create_job_linkedin()`: Creates job with LinkedIn URL and sourceUrl field
  - [ ] `test_list_user_jobs()`: Returns jobs filtered by userId
  - [ ] `test_filter_jobs_by_source_type()`: Filters jobs by "manual" or "linkedin_url"
  - [ ] `test_get_job_by_id()`: Retrieves single job with authorization check

- [ ] **Analysis Repository Tests:**
  - [ ] `test_create_analysis()`: Creates analysis with all fields (scores, recommendations, references)
  - [ ] `test_list_analyses_sort_by_date()`: Returns analyses sorted by analyzedAt desc
  - [ ] `test_list_analyses_sort_by_score()`: Returns analyses sorted by overallScore desc
  - [ ] `test_filter_analyses_by_cv()`: Filters analyses by cvId
  - [ ] `test_filter_analyses_by_job()`: Filters analyses by jobId
  - [ ] `test_filter_analyses_by_score_range()`: Filters analyses where minScore ≤ score ≤ maxScore
  - [ ] `test_pagination()`: Correctly implements limit/offset pagination
  - [ ] `test_get_analysis_by_id()`: Retrieves single analysis with authorization

- [ ] **User Data Deletion Tests:**
  - [ ] `test_delete_all_user_data()`: Deletes all CVs, jobs, analyses for userId
  - [ ] `test_delete_returns_count()`: Returns correct count of deleted items
  - [ ] `test_delete_wrong_user_no_effect()`: Doesn't delete other users' data

**Integration Tests (Backend API Endpoints):**

- [ ] **End-to-End Analysis Flow:**
  - [ ] `test_analyze_cv_creates_documents()`: POST /api/v1/analyze creates CV, job, analysis documents
  - [ ] `test_analyze_returns_ids()`: Response includes cvId, jobId, analysisId
  - [ ] `test_analyze_missing_user_id_header()`: Returns 401 when X-User-Id missing
  - [ ] `test_analyze_oversized_cv()`: Returns 400 when CV exceeds 100KB
  - [ ] `test_analyze_oversized_job()`: Returns 400 when job exceeds 50KB

- [ ] **API Endpoint Tests:**
  - [ ] `test_get_cvs_requires_auth()`: GET /api/v1/cvs returns 401 when userId header missing
  - [ ] `test_get_cvs_pagination()`: Limit/offset parameters work correctly
  - [ ] `test_get_cv_by_id_not_found()`: Returns 404 for non-existent CV
  - [ ] `test_get_cv_wrong_user()`: Returns 404 when userId mismatch (not 403)
  - [ ] `test_get_analyses_filter_by_score()`: Query params minScore/maxScore filter correctly
  - [ ] `test_delete_user_data()`: DELETE /api/v1/users/{userId}/data succeeds

- [ ] **Error Handling Tests:**
  - [ ] `test_database_unavailable_returns_503()`: All endpoints return 503 when Cosmos DB down
  - [ ] `test_health_check_shows_disconnected()`: GET /api/v1/health shows database status
  - [ ] `test_invalid_user_id_format()`: Returns 400 for malformed userId
  - [ ] `test_missing_required_fields()`: Returns 400 with field name when required field missing

**End-to-End Tests (Frontend + Backend + Database):**

- [ ] **User Journey: First Time User:**
  - [ ] Frontend generates new userId on first visit (stored in localStorage)
  - [ ] User uploads CV and analyzes → CV, job, analysis stored in Cosmos DB
  - [ ] User refreshes page → userId persists, can view analysis history
  - [ ] User clicks "Clear My Data" → all documents deleted, new userId generated

- [ ] **User Journey: Returning User:**
  - [ ] User returns to site → existing userId loaded from localStorage
  - [ ] Previous CVs and analyses displayed in history
  - [ ] User analyzes same CV against new job → new analysis created, references existing cvId
  - [ ] Analysis history shows both analyses with same CV

- [ ] **User Journey: Multi-CV Management:**
  - [ ] User uploads CV v1 → analyzes against Job A → score 62
  - [ ] User uploads CV v2 (revised) → analyzes against same Job A → score 78
  - [ ] History shows both analyses with different cvIds but same jobId
  - [ ] User can compare scores (visual indicator showing +16 improvement)

**Performance Tests:**

- [ ] **Query Performance:**
  - [ ] List 50 analyses: Completes in <100ms (p95 latency)
  - [ ] Get single analysis by ID: Completes in <50ms (partition-scoped query)
  - [ ] Create analysis: Completes in <100ms (including index updates)
  - [ ] All queries consume <10 RU each (partition-scoped, indexed fields)

- [ ] **Load Testing (Production):**
  - [ ] 100 concurrent analysis requests: Backend handles without throttling
  - [ ] 1,000 analyses/day: Cosmos DB RU consumption stays under budget (<100,000 RU/month)
  - [ ] Database initialization: Completes in <5 seconds on cold start

- [ ] **RU Consumption Monitoring:**
  - [ ] Create CV: Uses ~10 RU (2KB document)
  - [ ] Create analysis: Uses ~15 RU (5KB document with recommendations)
  - [ ] Query 10 analyses: Uses ~5 RU (partition-scoped, indexed)
  - [ ] Delete all user data (50 items): Uses ~50 RU (bulk delete)
  - [ ] Alert triggers at 50,000 RU/month (threshold configured in Azure Monitor)

**Local Development Tests:**

- [ ] **Docker Compose Setup:**
  - [ ] `docker-compose up -d`: Starts emulator and backend in <60 seconds
  - [ ] Emulator UI accessible at https://localhost:8081/_explorer
  - [ ] Backend health check shows "database: connected"
  - [ ] Database and container auto-created on first backend startup
  - [ ] Full CRUD operations work against emulator (no Azure subscription needed)

- [ ] **Developer Experience:**
  - [ ] New developer runs `git clone` → `docker-compose up` → `curl localhost:8000/api/v1/health` in <5 minutes
  - [ ] README includes troubleshooting for common emulator issues (SSL cert, port conflicts)
  - [ ] Backend logs clearly indicate local vs production environment

**Test Coverage Targets:**
- [ ] Backend repository layer: >90% code coverage
- [ ] API endpoints: >85% code coverage
- [ ] Critical paths (analyze, store, retrieve): 100% coverage

**Testing Tools:**
- Unit tests: `pytest` with `pytest-asyncio` for async operations
- Mocking: `pytest-mock` for Cosmos SDK mocking in unit tests
- Integration tests: Real Cosmos DB emulator (Docker container)
- E2E tests: `playwright` or `cypress` for frontend automation
- Load testing: `locust` or Azure Load Testing (production)
- Coverage: `pytest-cov` for coverage reports

**Priority:** P0 (Must Have - comprehensive testing ensures reliability)

---

### AC-DP8: Security and Validation (Phase 2)

- [ ] **Input Validation:**
  - [ ] User ID format validated (UUID v4 with "user-" prefix)
  - [ ] X-User-Id header matches query parameter userId in all endpoints
  - [ ] CV content size limited to 100KB (enforced, returns 400 if exceeded)
  - [ ] Job description size limited to 50KB (enforced)
  - [ ] Query parameters validated (limit 1-50, offset ≥0, sortBy/order whitelisted)
  - [ ] Missing required fields return 400 with specific error message

- [ ] **Security Measures:**
  - [ ] Cosmos DB connection string stored in Azure Key Vault (production)
  - [ ] App Service uses Managed Identity to access Key Vault (no credentials in code)
  - [ ] HTTPS enforced for all production endpoints (App Service configuration)
  - [ ] CORS configured to allow only frontend domain (not wildcard)
  - [ ] Data isolation: userId partition key prevents cross-user queries
  - [ ] Authorization: All endpoints verify userId in header matches query parameter
  - [ ] No connection strings or secrets committed to Git (`.env` in `.gitignore`)

- [ ] **Error Handling:**
  - [ ] Database unavailable: Returns 503 with user-friendly message
  - [ ] Item not found: Returns 404 (not 500)
  - [ ] Unauthorized access: Returns 401 (missing userId) or 404 (userId mismatch)
  - [ ] Invalid input: Returns 400 with specific validation error
  - [ ] All errors logged with full context (userId, endpoint, error details)

**Priority:** P0 (Must Have - security and data integrity critical)

---

## Out of Scope

The following features are explicitly **NOT included** in Phase 2 data persistence implementation:

### Phase 2 Exclusions

1. **User Authentication & Multi-Device Sync**
   - No login/registration system
   - No email/password accounts
   - No OAuth integration (Google, Microsoft, LinkedIn)
   - No cross-device data access (session locked to browser)
   - **Future:** Phase 3 will add authentication for multi-device sync

2. **Advanced History Features**
   - No side-by-side analysis comparison UI
   - No score trend graphs or progress dashboards
   - No recommendation implementation tracking ("Mark as Done")
   - **Future:** Phase 3 analytics features

3. **Data Export**
   - No "Download My Data" button (GDPR compliance feature)
   - No JSON/PDF export of analyses
   - No bulk CV/job export
   - **Dev Lead Decision (Q2):** Defer data export API to Phase 3 due to scope constraints
   - **Future:** Phase 3 export functionality (JSON/PDF download)

4. **Data Migration Tools**
   - No import from other CV analysis tools
   - No bulk upload of past analyses
   - No data format conversion utilities
   - **Future:** Only if user demand warrants

5. **Automated Data Retention Policies**
   - No auto-deletion of analyses older than X days
   - No storage quota limits per user
   - No archival/compression of old data
   - **Future:** Phase 3 with usage-based policies

6. **Collaborative Features**
   - No sharing analyses with others (via link or email)
   - No team/organization accounts (career coaches managing multiple clients)
   - No commenting or notes on analyses
   - **Future:** Phase 3 for career coach persona

7. **Data Backup & Recovery**
   - No user-initiated backup downloads
   - No "Undo Delete" or trash/recycle bin
   - **Azure handles:** Server-side backups (Cosmos DB automatic backups)

8. **Advanced Querying**
   - No full-text search across CVs or job descriptions
   - No tagging/categorization of analyses
   - No custom filters (e.g., "Show all analyses for Python jobs")
   - **Future:** Only if usage patterns show demand

---

### Future Considerations (Phase 3+)

**Authentication & User Accounts (High Priority)**
- Email/password registration
- OAuth integration (LinkedIn, Google)
- Multi-device sync (same account, multiple browsers/devices)
- Password reset and account recovery

**Enhanced Analytics (Medium Priority)**
- Score trend visualization (line graph over time)
- Comparative analysis (CV v1 vs CV v2 against same job)
- Recommendation implementation tracking (checkbox "Done")
- Average score by job category (if categorization added)

**Data Portability (GDPR Compliance - High Priority if EU users)**
- "Download My Data" button (JSON export)
- PDF export of individual analyses
- Bulk export of all analyses
- Automated deletion after X months (configurable)

**Team/Organization Features (For Career Coaches - Low Priority for MVP)**
- Multi-user accounts (coach manages multiple client CVs)
- Shared analysis workspace
- Client progress dashboards
- Invoice generation based on analysis count

---

**End of Document**
