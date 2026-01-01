# CV Checker - Frontend-Backend Integration Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│                        (React + Zustand + Vite)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND COMPONENTS                              │
│  ┌─────────────┐  ┌──────────────────┐  ┌─────────────────────────┐  │
│  │  CVUpload   │  │JobDescriptionInput│  │  ConnectionStatus      │  │
│  │             │  │                  │  │                         │  │
│  │ • File drop │  │ • Text area      │  │ • Health check         │  │
│  │ • Validate  │  │ • Validation     │  │ • Auto-test on mount   │  │
│  │ • Store     │  │ • Store          │  │ • Retry button         │  │
│  └─────────────┘  └──────────────────┘  └─────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      AnalyzeButton                                │  │
│  │  • Prerequisites check                                           │  │
│  │  • Trigger analysis                                              │  │
│  │  • Loading/error states                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         STATE MANAGEMENT (Zustand)                       │
│                                                                          │
│  ┌────────────────┐  ┌─────────────────┐  ┌────────────────────┐     │
│  │   currentCV    │  │   currentJob    │  │     analysis       │     │
│  │ • filename     │  │ • description   │  │ • isLoading       │     │
│  │ • content      │  │ • lastModified  │  │ • error           │     │
│  │ • uploadedAt   │  │ • sourceType    │  │ • result          │     │
│  └────────────────┘  └─────────────────┘  └────────────────────┘     │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │                      history: AnalysisHistory[]                  │  │
│  │  • Persisted to localStorage                                    │  │
│  │  • Last 10 analyses                                             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER                                       │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              AnalysisService                                      │  │
│  │  ┌───────────────────────────────────────────────────────────┐  │  │
│  │  │ analyze(input)                                            │  │  │
│  │  │   1. Sanitize inputs (whitespace, line endings)           │  │  │
│  │  │   2. Validate inputs (length, content)                    │  │  │
│  │  │   3. Call API client                                      │  │  │
│  │  │   4. Handle success/error                                 │  │  │
│  │  │   5. Return structured result                             │  │  │
│  │  └───────────────────────────────────────────────────────────┘  │  │
│  │                                                                   │  │
│  │  • testConnection() → Health check                               │  │
│  │  • getAPIBaseURL() → Debug info                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API CLIENT (Axios)                                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                Request Interceptor                                │  │
│  │  • Add X-Request-ID header                                       │  │
│  │  • Log request details                                           │  │
│  │  • Add timestamp                                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    HTTP Methods                                   │  │
│  │  • healthCheck() → GET /api/v1/health (5s timeout)              │  │
│  │  • analyze() → POST /api/v1/analyze (90s timeout)               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │               Response Interceptor                                │  │
│  │  • Log response status and duration                              │  │
│  │  • Extract error messages                                        │  │
│  │  • Retry logic (up to 2 retries):                               │  │
│  │    - Network errors → Retry                                      │  │
│  │    - 5xx server errors → Retry with backoff                     │  │
│  │    - 429 rate limit → Retry with backoff                        │  │
│  │  • Return user-friendly error messages                           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                         HTTP (JSON over REST)
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     BACKEND API (FastAPI)                                │
│                    http://localhost:8000                                 │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ GET /api/v1/health                                               │  │
│  │  → {status, version, service, azure_openai, cosmos_db}          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │ POST /api/v1/analyze                                             │  │
│  │  Request: {cv_markdown, job_description}                         │  │
│  │                                                                   │  │
│  │  Process:                                                         │  │
│  │    1. JobParser → Extract job requirements                       │  │
│  │    2. CVParser → Extract candidate profile                       │  │
│  │    3. Analyzer → Hybrid scoring (60% deterministic + 40% LLM)   │  │
│  │    4. ReportGenerator → Create recommendations                   │  │
│  │                                                                   │  │
│  │  Response: {                                                      │  │
│  │    analysis_id,                                                   │  │
│  │    overall_score,                                                 │  │
│  │    skill_matches[],                                              │  │
│  │    experience_match,                                              │  │
│  │    education_match,                                               │  │
│  │    strengths[],                                                   │  │
│  │    gaps[],                                                        │  │
│  │    recommendations[]                                              │  │
│  │  }                                                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   AI AGENT FRAMEWORK                                     │
│                  (Microsoft Agent Framework)                             │
│                                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ JobParser  │→ │  CVParser  │→ │  Analyzer  │→ │ReportGenerator │  │
│  │            │  │            │  │            │  │                │  │
│  │ Extract    │  │ Extract    │  │ Hybrid     │  │ Generate       │  │
│  │ job reqs   │  │ candidate  │  │ scoring    │  │ recommendations│  │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     AZURE OPENAI                                         │
│                    (GPT-4 via Entra ID)                                 │
│                                                                          │
│  • Model: GPT-4-1                                                       │
│  • Auth: DefaultAzureCredential (Entra ID)                              │
│  • Semantic analysis, soft skills evaluation                            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────┐
│  User Action    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│  API Call (analyze)                     │
└────────┬────────────────────────────────┘
         │
         ▼
    ┌────────────┐
    │  Success?  │
    └────┬───┬───┘
         │   │
    Yes  │   │  No
         │   │
         │   └──────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐   ┌──────────────────────┐
│ Return result   │   │  Error Type?         │
└─────────────────┘   └──────┬───────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────────┐ ┌────────┐  ┌─────────────┐
     │ Network Error  │ │422     │  │ 5xx / 429   │
     │ (no response)  │ │Validate│  │ Server Error│
     └───────┬────────┘ └───┬────┘  └──────┬──────┘
             │              │               │
             ▼              ▼               ▼
     ┌────────────────┐ ┌────────┐  ┌─────────────┐
     │Show "Cannot    │ │Show     │  │Retry up to  │
     │connect..."     │ │field    │  │2 times with │
     │+ Retry button  │ │errors   │  │backoff      │
     └────────────────┘ └────────┘  └──────┬──────┘
                                            │
                                     ┌──────┴──────┐
                                     │             │
                                Success         Fail
                                     │             │
                                     ▼             ▼
                             ┌───────────┐  ┌────────────┐
                             │Return     │  │Show error  │
                             │result     │  │+ Retry btn │
                             └───────────┘  └────────────┘
```

## State Management Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ZUSTAND STORE                                    │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    User Actions                                   │  │
│  │                                                                   │  │
│  │  uploadCV(filename, content)                                     │  │
│  │    → currentCV = {filename, content, uploadedAt}                 │  │
│  │    → Persisted to localStorage                                   │  │
│  │                                                                   │  │
│  │  updateJobDescription(description, type, url?)                   │  │
│  │    → currentJob = {description, lastModified, sourceType, url}   │  │
│  │    → Persisted to localStorage                                   │  │
│  │                                                                   │  │
│  │  startAnalysis()                                                  │  │
│  │    → analysis.isLoading = true                                   │  │
│  │    → analysis.error = null                                       │  │
│  │    → analysis.result = null                                      │  │
│  │                                                                   │  │
│  │  completeAnalysis(result)                                         │  │
│  │    → analysis.isLoading = false                                  │  │
│  │    → analysis.result = result                                    │  │
│  │    → Add to history[] (last 10)                                  │  │
│  │    → Persist history to localStorage                             │  │
│  │    → currentView = 'results'                                     │  │
│  │                                                                   │  │
│  │  failAnalysis(error)                                              │  │
│  │    → analysis.isLoading = false                                  │  │
│  │    → analysis.error = error                                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  Persistence (localStorage)                       │  │
│  │                                                                   │  │
│  │  Key: 'cv-checker-storage'                                       │  │
│  │  Persisted:                                                       │  │
│  │    • currentCV                                                    │  │
│  │    • currentJob                                                   │  │
│  │    • history (max 10 analyses)                                   │  │
│  │                                                                   │  │
│  │  Not Persisted (session-only):                                   │  │
│  │    • analysis (isLoading, error, result)                         │  │
│  │    • currentView                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
App
├── UploadView (when currentView === 'upload')
│   ├── ConnectionStatus (auto-tests backend)
│   ├── CVUpload
│   │   ├── File drag/drop zone
│   │   ├── Validation (file type, size, content)
│   │   └── Success display with filename
│   ├── JobDescriptionInput
│   │   ├── JobInputModeToggle (manual vs LinkedIn URL)
│   │   ├── Textarea with character counter
│   │   ├── LinkedInURLInput (optional)
│   │   └── Validation (length, content)
│   └── AnalyzeButton
│       ├── Prerequisites checklist
│       ├── Loading state with spinner
│       └── Error display with retry
│
├── ResultsDisplay (when currentView === 'results')
│   ├── Overall score gauge
│   ├── Skill matches table
│   ├── Strengths list
│   ├── Gaps list
│   └── Recommendations list
│
└── AnalysisHistory (when currentView === 'history')
    ├── History item list
    ├── Score badges
    └── Click to view past results
```

## Request/Response Cycle

```
┌──────────────┐
│ User clicks  │
│"Analyze Match"│
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ useAppStore.startAnalysis()  │
│  → isLoading = true          │
└──────┬───────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│ AnalysisService.analyze()              │
│  1. Sanitize inputs                    │
│  2. Validate inputs                    │
│  3. Build request object               │
└──────┬─────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│ api.analyze(request)                   │
│  • Add request ID header               │
│  • Log request                         │
│  • POST /api/v1/analyze                │
│  • Wait up to 90 seconds               │
└──────┬─────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│ Backend processes (20-40 seconds)      │
│  1. JobParser extracts requirements    │
│  2. CVParser extracts profile          │
│  3. Analyzer scores compatibility      │
│  4. ReportGenerator creates advice     │
└──────┬─────────────────────────────────┘
       │
       ▼
┌────────────────────────────────────────┐
│ Response received                      │
│  • Log response                        │
│  • Extract data                        │
└──────┬─────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│ useAppStore.completeAnalysis(result)     │
│  → isLoading = false                     │
│  → result = {...}                        │
│  → Add to history                        │
│  → Navigate to results view              │
└──────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│ Results display  │
│ with full data   │
└──────────────────┘
```

## Key Integration Points

1. **Environment Config** → API base URL from `.env`
2. **Type Safety** → TypeScript types match backend exactly
3. **State Management** → Zustand for reactive updates
4. **Persistence** → localStorage for CV, job, history
5. **Error Handling** → Retry logic + user-friendly messages
6. **Loading States** → Real-time UI feedback
7. **Validation** → Client-side before API call
8. **Logging** → Console logs for debugging
9. **Connection Test** → Auto-check on mount
10. **History Tracking** → Last 10 analyses saved

---

**Phase 3 Complete:** All components connected and ready for testing with Azure OpenAI!
