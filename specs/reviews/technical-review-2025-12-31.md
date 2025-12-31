# Technical Review: CV Checker PRD v1.0

**Reviewer:** Development Lead  
**Review Date:** December 31, 2025  
**PRD Version:** 1.0  
**Status:** APPROVED WITH MODIFICATIONS REQUIRED  

---

## Executive Summary

The PRD is **well-structured and comprehensive**, demonstrating strong product thinking and clear user focus. The proposed technical stack (Python/FastAPI, Microsoft Agent Framework, Azure OpenAI, Cosmos DB) is **sound and feasible** for the stated requirements.

**Overall Assessment: 7.5/10**

**Verdict:** Proceed with **critical modifications** listed in Section 3. The 5-agent architecture may be **over-engineered for MVP** – recommend simplification (see Section 6). Several technical requirements need clarification before development starts.

**Key Concerns:**
1. ⚠️ **5-agent architecture is complex for MVP** – recommend 2-3 agents initially
2. ⚠️ **Missing critical API requirements** (rate limiting, authentication, CORS)
3. ⚠️ **Cosmos DB partition key strategy undefined**
4. ⚠️ **No error handling specifications for AI failures**
5. ⚠️ **Unclear sync vs. async processing decision**
6. ⚠️ **Missing observability and monitoring requirements**
7. ⚠️ **No cost estimation or budget constraints**

---

## 1. Technical Feasibility Assessment ✅

### 1.1 Technology Stack Validation

| Component | Proposed Technology | Assessment | Notes |
|-----------|-------------------|------------|-------|
| **Backend Framework** | FastAPI (Python 3.11+) | ✅ **Excellent** | Fast, modern, auto OpenAPI docs, great for AI workloads |
| **Agent Framework** | Microsoft Agent Framework | ⚠️ **NEEDS VALIDATION** | Confirm version, maturity, and Python support |
| **AI Service** | Azure OpenAI (GPT-4o) | ✅ **Excellent** | Proven for semantic analysis, structured output support |
| **Database** | Azure Cosmos DB (NoSQL) | ✅ **Good** | Flexible schema, but partition key strategy critical |
| **Hosting** | Azure App Service / Container Apps | ✅ **Good** | Container Apps preferred for scalability |
| **Frontend** | AG-UI | ⚠️ **NEEDS RESEARCH** | Unknown framework maturity – validate before Phase 2 |

**Overall Feasibility: HIGH (8/10)**

### 1.2 Critical Validation Required

**BLOCKER QUESTIONS (Must resolve in Week 1):**

1. **Microsoft Agent Framework:**
   - Which specific library/package? (`semantic-kernel`, `autogen`, custom framework?)
   - Python support confirmed?
   - Production-ready or experimental?
   - **ACTION:** Research and document in ADR-001

2. **AG-UI Framework:**
   - Is this an internal Microsoft framework?
   - Public documentation available?
   - Component library maturity?
   - **ACTION:** Validate feasibility before committing to Phase 2 timeline

3. **Azure OpenAI Quotas:**
   - What is current GPT-4o TPM (tokens per minute)?
   - Expected token usage per analysis? (~5K-10K tokens estimated)
   - Do we need quota increase for 100 concurrent users?
   - **ACTION:** Calculate requirements and request quota in Week 1

---

## 2. What's Good ✅

### 2.1 Strong Product Foundation
- **Clear user personas** with realistic usage patterns
- **Well-defined problem statement** and value propositions
- **Appropriate phased approach** (MVP → UI → Advanced)
- **Comprehensive feature breakdown** with priorities

### 2.2 Solid Technical Choices
- **FastAPI** is perfect for AI APIs (async support, validation, OpenAPI)
- **Azure OpenAI** with structured output is ideal for parsing tasks
- **Cosmos DB** provides flexibility for evolving schema
- **Agent-based architecture** aligns with modern AI application patterns

### 2.3 Good Engineering Practices
- **Markdown-only MVP** is smart (simplest parsing, iterate later)
- **Manual job input first** avoids scraping complexity
- **Clear data models** with JSON schemas
- **Acceptance criteria** are specific and testable
- **Risk identification** shows thoughtful planning

### 2.4 Excellent Documentation
- **API endpoint specs** are clear and RESTful
- **Agent responsibilities** well-defined
- **Success metrics** include both business and technical KPIs
- **Out-of-scope** section prevents feature creep

---

## 3. Critical Gaps & Missing Requirements 🚨

### 3.1 API & Infrastructure Requirements

#### **MISSING: API Security & Limits**
```yaml
REQUIRED ADDITIONS:

1. Rate Limiting
   - Per-IP rate limits: 10 requests/minute for uploads, 5 analyses/minute
   - Global rate limit: 100 concurrent analyses
   - 429 Too Many Requests response with Retry-After header
   
2. CORS Configuration
   - Allowed origins for Phase 2 frontend
   - Credential handling for future auth
   
3. Request Validation
   - Max CV file size: 2MB (specified) ✅
   - Max job description length: 50K chars (specified) ✅
   - ADD: Timeout for analysis requests (30s max)
   - ADD: Request ID for tracing
   
4. API Versioning
   - /api/v1 prefix (specified) ✅
   - ADD: Version deprecation policy
```

**ACTION:** Add FR1.5 (Rate Limiting) and FR1.6 (Security Headers) to PRD

---

#### **MISSING: Error Handling Specifications**

Current PRD mentions "error handling" but lacks detail. **REQUIRED:**

```python
# Error Response Schema (ADD TO PRD)
{
  "error": {
    "code": "string (ERROR_CODE)",
    "message": "string (user-friendly)",
    "details": "string (optional technical details)",
    "request_id": "string (correlation ID)",
    "timestamp": "datetime (ISO 8601)"
  }
}

# Error Codes (DEFINE IN PRD):
- CV_UPLOAD_FAILED
- CV_TOO_LARGE
- CV_INVALID_FORMAT
- JOB_DESCRIPTION_TOO_LONG
- JOB_DESCRIPTION_EMPTY
- ANALYSIS_TIMEOUT
- AI_SERVICE_UNAVAILABLE
- ANALYSIS_NOT_FOUND
- INTERNAL_SERVER_ERROR
```

**Specific Scenarios to Document:**

1. **Azure OpenAI Failures:**
   - What if OpenAI API is down? (Fallback strategy?)
   - What if token limit exceeded? (Truncate input?)
   - What if structured output parsing fails? (Retry? Manual parsing?)

2. **Agent Failures:**
   - If CV Parser fails, can we proceed with raw text?
   - If Analyzer fails, do we return partial results?
   - Retry logic per agent (currently "3 attempts" mentioned – good!)

3. **Database Failures:**
   - What if Cosmos DB write fails after analysis completes?
   - Transaction strategy for multi-document writes?

**ACTION:** Add Section 8.5 "Error Handling Requirements" to PRD

---

### 3.2 Data & Storage Requirements

#### **CRITICAL: Cosmos DB Partition Key Strategy**

PRD has "Open Question #5" but this is **BLOCKING for Week 1**. 

**Recommendation:**

```yaml
Partition Key Strategy:

Option A (RECOMMENDED for Phase 1):
  partition_key: "/id"  # Each document is its own partition
  pros: 
    - Simple implementation
    - No hot partitions
    - Works without user authentication
  cons:
    - Cannot query across CVs efficiently (not needed in Phase 1)
    - Less efficient for user-based queries (Phase 3)
  
Option B (Future-proof for Phase 3):
  partition_key: "/user_id"  # Partition by user
  pros:
    - Efficient user queries in Phase 3
    - Logical data grouping
  cons:
    - Requires synthetic user_id in Phase 1 (e.g., "anonymous")
    - Risk of hot partitions if one user has thousands of analyses
  
DECISION: Use Option A for Phase 1, migrate to Option B in Phase 3 (documented migration path)
```

**ACTION:** Replace "Open Question #5" with decided partition key strategy in PRD Section 5 (Technical Architecture)

---

#### **MISSING: Data Retention & Cleanup Policy**

PRD mentions "Open Question #4" but provides no default. **REQUIRED for MVP:**

```yaml
Data Retention Policy (Phase 1 - Anonymous):

CVs:
  - Retention: 30 days from upload
  - Cleanup: Daily batch job deletes CVs older than 30 days
  - Rationale: Anonymous users may return, but not long-term storage
  
Job Descriptions:
  - Retention: 30 days from submission
  - Cleanup: Same as CVs
  - Rationale: Job postings change frequently
  
Analyses:
  - Retention: 90 days from creation
  - Cleanup: Daily batch job
  - Rationale: Historical comparisons useful, but not indefinitely
  
Orphaned Data:
  - If CV is deleted, cascade delete all associated analyses
  - If Job is deleted, keep analyses (for history)

Implementation:
  - TTL (Time-to-Live) feature in Cosmos DB
  - Set TTL on document creation
  - No manual cleanup scripts needed
```

**ACTION:** Add FR5.4 "Data Retention Policy" to Feature 5 (Analysis History)

---

#### **MISSING: File Storage Strategy**

PRD stores CV "content" as string in Cosmos DB. For Markdown, this works. But:

**Issue:** When Phase 3 adds PDF/DOCX:
- Binary files cannot be stored as JSON strings in Cosmos DB
- 2MB Cosmos DB item limit may be tight for large PDFs

**Recommendation:**

```yaml
File Storage (FUTURE-PROOF):

Phase 1 (Markdown):
  - Store content directly in Cosmos DB ✅ (already planned)
  - Works fine for text-based formats
  
Phase 3 (PDF/DOCX):
  - Store files in Azure Blob Storage
  - Store blob URL + parsed text in Cosmos DB
  - Keeps Cosmos DB lean, supports larger files
  
Schema Update (ADD TO PRD):
{
  "id": "uuid",
  "content": "string (text content or parsed text)",
  "storage": {
    "type": "inline | blob",
    "blob_url": "string (if type=blob, optional)"
  },
  "format": "markdown | pdf | docx"
}
```

**ACTION:** Document storage strategy in data models (Section 5.2) with Phase 3 migration note

---

### 3.3 AI & Agent Requirements

#### **MISSING: Token Usage & Cost Management**

PRD mentions "token usage optimized" but no specifics. **REQUIRED:**

```yaml
Token Usage Budget (Per Analysis):

Estimated Token Usage:
  - CV Parser: 1000 (input) + 500 (output) = 1500 tokens
  - Job Parser: 800 (input) + 400 (output) = 1200 tokens
  - Analyzer: 1500 (input) + 800 (output) = 2300 tokens
  - Report Generator: 1000 (input) + 1200 (output) = 2200 tokens
  - Total per analysis: ~7200 tokens
  
Cost Calculation (GPT-4o pricing ~$5/1M input, $15/1M output):
  - Input tokens: 4300 * $5/1M = $0.0215
  - Output tokens: 2900 * $15/1M = $0.0435
  - Total per analysis: ~$0.065
  - For 10K analyses/day: ~$650/day = ~$20K/month
  
Budget Constraints:
  - Set max_tokens limits per agent call
  - Implement token counting before requests
  - Alert if daily costs exceed threshold
  - Consider caching for repeated job descriptions
```

**ACTION:** Add Section 8.6 "Cost Management" to PRD with token budgets and alerts

---

#### **MISSING: Prompt Engineering Guidelines**

PRD describes "AI Prompt Strategy" per agent but lacks:
- Prompt templates (even rough drafts)
- Few-shot examples structure
- Prompt versioning strategy
- A/B testing plan for prompt optimization

**Recommendation:**

```yaml
Prompt Management (ADD TO PRD):

1. Prompt Storage:
   - Store prompts in separate files (prompts/cv_parser.txt)
   - Version control with Git
   - Load prompts at runtime (configurable)
   
2. Prompt Structure:
   - System prompt (role, instructions, output format)
   - Few-shot examples (2-3 examples per task)
   - User prompt (actual CV or job description)
   
3. Prompt Versioning:
   - Tag prompts with version (v1, v2)
   - Track which prompt version used in each analysis
   - Enable A/B testing of prompt improvements
   
4. Evaluation:
   - Golden test set (20 CV-job pairs)
   - Automated scoring against expected outputs
   - Regression testing when prompts change
```

**ACTION:** Add FR3.6 "Prompt Management" and create ADR-002 for prompt engineering approach

---

#### **MISSING: Structured Output Schema Validation**

PRD mentions "JSON mode" for Azure OpenAI but doesn't specify:
- Exact JSON schemas for each agent output
- What if AI returns invalid JSON?
- Pydantic models for validation?

**Recommendation:**

```python
# ADD TO PRD (Section 5.2 Data Models):

# CV Parser Output Schema (Pydantic Model)
class CVParserOutput(BaseModel):
    sections: CVSections
    metadata: CVMetadata
    
    class Config:
        extra = "forbid"  # Reject unexpected fields

# Validation Strategy:
1. Use Azure OpenAI JSON Schema mode (structured outputs)
2. Validate with Pydantic models
3. If validation fails:
   - Retry with same prompt (1 attempt)
   - If still fails, log error and return generic parsing
   - Never fail entire analysis due to parsing
```

**ACTION:** Add Pydantic models to data model section, document validation strategy

---

### 3.4 Observability & Monitoring

#### **MISSING: Logging Requirements**

PRD mentions "structured logging with correlation IDs" (good!) but lacks:
- What to log at each stage?
- Log levels (INFO, ERROR, DEBUG)?
- PII handling in logs (CVs contain personal data)?

**Recommendation:**

```yaml
Logging Requirements (ADD TO PRD):

1. Structured Logging Format:
   - JSON logs with correlation_id, timestamp, level, message
   - Use Python structlog library
   
2. Log Levels:
   - INFO: API requests, agent start/complete, analysis results
   - ERROR: Failures, retries, timeouts
   - DEBUG: Detailed agent inputs/outputs (exclude in production)
   
3. PII Handling:
   - NEVER log full CV content (contains names, emails, addresses)
   - Log only metadata (cv_id, file_size, sections_found)
   - Sanitize job descriptions (remove company names if needed)
   
4. Correlation IDs:
   - Generate UUID per API request
   - Pass through all agents
   - Include in all log entries
   - Return in API response for debugging
   
5. Log Retention:
   - Application logs: 30 days in Application Insights
   - Error logs: 90 days
   - Debug logs: 7 days (only if enabled)
```

**ACTION:** Add FR8.1 "Logging Requirements" to new Section 8 "Non-Functional Requirements"

---

#### **MISSING: Metrics & Alerts**

PRD defines success metrics but not **operational metrics** for monitoring. **REQUIRED:**

```yaml
Operational Metrics (ADD TO PRD):

1. API Metrics:
   - Request rate (requests/second)
   - Response time (p50, p95, p99)
   - Error rate (4xx, 5xx)
   - Active connections
   
2. Agent Metrics:
   - Agent execution time per type
   - Agent success/failure rate
   - Retry count per agent
   - Token usage per agent
   
3. Azure OpenAI Metrics:
   - Token consumption rate
   - API call latency
   - Rate limit hits (429 errors)
   - Daily cost
   
4. Database Metrics:
   - Query latency
   - RU (Request Unit) consumption
   - Throttling events (429 from Cosmos)
   - Storage size
   
5. Alerts (Azure Monitor):
   - Critical: API error rate >5% (5 min window)
   - Critical: Analysis timeout rate >10%
   - Warning: Daily OpenAI cost >$1000
   - Warning: Cosmos DB RU usage >80%
   - Info: Unusual traffic spike (2x baseline)
```

**ACTION:** Add Section 8.2 "Monitoring Requirements" to PRD

---

### 3.5 Testing Requirements

PRD mentions testing but lacks detail. **REQUIRED:**

```yaml
Testing Requirements (EXPAND IN PRD):

1. Unit Tests:
   - Each agent function tested independently
   - Mock Azure OpenAI calls (use fixtures)
   - Mock Cosmos DB calls
   - Target: 80% code coverage ✅ (already specified)
   
2. Integration Tests:
   - Test agent orchestration end-to-end
   - Use Azure OpenAI test endpoint (not prod)
   - Use Cosmos DB emulator locally
   - Verify data persistence
   
3. API Tests:
   - All endpoints tested with valid/invalid inputs
   - Test error responses (400, 404, 500)
   - Test rate limiting
   - Use pytest + FastAPI TestClient
   
4. Load Tests:
   - 100 concurrent analyses (specified) ✅
   - Measure response time degradation
   - Identify bottlenecks (AI calls, DB writes)
   - Tool: Locust or Azure Load Testing
   
5. AI Quality Tests (NEW):
   - Golden test set: 20 CV-job pairs with expected scores
   - Automated scoring: "Does actual score match expected ±10?"
   - Recommendation relevance: Manual review of sample outputs
   - Regression testing: Run on every prompt change
   
6. End-to-End Tests:
   - Upload CV → Submit Job → Analyze → Retrieve Results
   - Test full user workflow
   - Run in staging environment before production
```

**ACTION:** Expand Section 7 "Acceptance Criteria" with detailed testing requirements

---

## 4. Technical Risks Not Addressed ⚠️

### 4.1 AI Reliability Risks

| Risk | Severity | Likelihood | Mitigation (ADD TO PRD) |
|------|----------|------------|------------------------|
| **Hallucination:** AI invents skills not in CV/job | High | Medium | Validate AI outputs against source text; implement fact-checking layer |
| **Inconsistent scoring:** Same CV+job gets different scores | Medium | High | Add temperature=0 to OpenAI calls; test score variance; document acceptable range (±5 points) |
| **Prompt injection:** User CV contains adversarial text to manipulate score | Medium | Low | Sanitize inputs; use system-level instructions; monitor for unusual outputs |
| **Non-English content:** CV/job in other languages fails parsing | Low | Medium | Phase 1: Document English-only; Phase 3: Add language detection |

**ACTION:** Add Section 9 "AI Risk Mitigation" to PRD

---

### 4.2 Performance Risks

| Risk | Severity | Likelihood | Mitigation (ADD TO PRD) |
|------|----------|------------|------------------------|
| **Azure OpenAI latency spikes:** API calls take >10s | High | Medium | Set timeouts (10s per call); implement retries; use async calls where possible |
| **Sequential agent execution is slow:** 5 agents = 5 serial API calls | High | High | See Section 6 (simplify architecture) OR parallelize where possible |
| **Cosmos DB partition hotspots:** If using /user_id with heavy users | Medium | Low | Use /id partition key (recommended in 3.2) |
| **Large CV/job parsing timeout:** 50K char job description | Medium | Medium | Truncate inputs to max length (define max); optimize prompts for token efficiency |

**ACTION:** Document performance mitigations in Section 8.3 "Performance Requirements"

---

### 4.3 Data Consistency Risks

| Risk | Severity | Likelihood | Mitigation (ADD TO PRD) |
|------|----------|------------|------------------------|
| **Analysis saved but CV/job reference deleted** | Medium | Low | Implement soft deletes; or store essential data in analysis doc |
| **Concurrent analyses on same CV corrupt state** | Low | Low | Cosmos DB handles concurrency; no shared state across analyses |
| **Agent failure leaves incomplete analysis** | Medium | Medium | Wrap orchestrator in try/catch; save partial results OR mark as failed |

**ACTION:** Document transaction handling in Section 8.4 "Data Consistency"

---

## 5. Complexity Assessment 📊

### 5.1 Scope Appropriateness

**Phase 1 (6 weeks): AGGRESSIVE BUT ACHIEVABLE**

Complexity Breakdown:
- **Week 1-2:** Setup (Azure resources, FastAPI scaffold, agent framework) – **MEDIUM**
- **Week 3-4:** Agent implementation (5 agents, prompts, orchestration) – **HIGH**
- **Week 5:** Integration & testing – **HIGH**
- **Week 6:** Performance tuning & documentation – **MEDIUM**

**Assessment:** 6 weeks is **tight but feasible** IF:
1. Team has Azure & FastAPI experience
2. Agent framework is well-documented
3. No major blockers in OpenAI quota or Cosmos DB setup
4. Scope is strictly limited (no Phase 2 features)

**Recommendation:** Add 1-week buffer (7 weeks total) for unknowns.

---

**Phase 2 (4 weeks): FEASIBLE IF AG-UI IS MATURE**

Complexity Breakdown:
- **Week 7-8:** Frontend scaffolding, CV upload, job input – **MEDIUM**
- **Week 9:** Results visualization, history view – **MEDIUM**
- **Week 10:** Testing, polish, deployment – **MEDIUM**

**Assessment:** 4 weeks is **reasonable** if AG-UI has:
- Good documentation
- Component library for forms, visualizations
- Clear examples

**Risk:** If AG-UI is experimental or poorly documented, add 2 weeks.

**Recommendation:** Prototype AG-UI in Week 1-2 to validate feasibility. If problematic, pivot to React + shadcn/ui.

---

### 5.2 Feature Prioritization

**Current P0 (Must Have) features are well-chosen.** However:

**Consider downgrading:**
- **FR2.3 (Job Description Preprocessing):** P1 → P2
  - Rationale: AI models handle messy text well. Preprocessing adds complexity.
  - Simplify: Just validate length and non-empty. Let AI handle formatting.

- **FR3.4 (Experience Alignment):** P1 → P1 (keep, but simplify scoring)
  - Rationale: Years of experience matching is complex (parsing "5+ years", "3-5 years").
  - Simplify: Extract if present, but don't penalize if missing.

- **FR4.5 (Content to Remove):** P1 → P2
  - Rationale: Negative feedback ("remove this") may demotivate users.
  - Simplify: Focus on "add" and "emphasize" in MVP.

**ACTION:** Review and adjust feature priorities in PRD based on recommendations above.

---

## 6. Agent Design Evaluation 🤖

### 6.1 Current 5-Agent Architecture

```
Orchestrator → CV Parser → Job Parser → Analyzer → Report Generator
                    ↓           ↓            ↓              ↓
                                    Azure OpenAI (4 calls)
```

**Analysis:**
- **5 agents = 4 sequential Azure OpenAI API calls (CV Parser, Job Parser, Analyzer, Report Generator)**
- **Estimated latency:** 4 calls × 5-7s avg = **20-28 seconds** (within 30s target, but tight)
- **Complexity:** High for MVP – more code, more testing, more points of failure

**Pros:**
- ✅ Separation of concerns (clean architecture)
- ✅ Each agent is focused and testable
- ✅ Easy to swap out agents (e.g., improve CV Parser independently)
- ✅ Aligns with Microsoft Agent Framework best practices

**Cons:**
- ❌ **Over-engineered for MVP** (adds 2-3 weeks of development time)
- ❌ Sequential execution is slow (cannot easily parallelize)
- ❌ More failure points (5 agents vs. 2-3)
- ❌ Higher token costs (5 calls have prompt overhead vs. 2-3)

---

### 6.2 Recommendation: SIMPLIFY TO 3 AGENTS FOR PHASE 1

**Proposed Simplified Architecture:**

```
┌─────────────────────────────────────┐
│      Orchestrator Agent             │
│  (Workflow coordination only)       │
└────────┬──────────────┬─────────────┘
         │              │
         ▼              ▼
    ┌────────┐    ┌──────────┐
    │Analysis│    │ Storage  │
    │ Agent  │    │  Agent   │
    └────────┘    └──────────┘
         │
    Azure OpenAI
    (1-2 calls)
```

**Changes:**

1. **Merge CV Parser + Job Parser + Analyzer into single "Analysis Agent"**
   - One AI call with combined prompt:
     ```
     Input: CV text + Job text
     Output: {
       parsed_cv: {...},
       parsed_job: {...},
       scores: {...},
       gaps: {...}
     }
     ```
   - **Benefit:** 1 API call instead of 3 → faster, cheaper, simpler
   - **Trade-off:** Less modular, but acceptable for MVP

2. **Keep Report Generator as separate agent**
   - Rationale: Recommendation generation is complex enough to warrant separation
   - Input: Analysis results
   - Output: Recommendations JSON

3. **Orchestrator remains lightweight**
   - Coordinates Analysis Agent → Report Generator → Storage Agent
   - Handles errors and retries

**Revised Latency:**
- 2 AI calls × 6s avg = **~12 seconds** (50% faster!)
- Better user experience

**Development Time Savings:**
- Reduce from 5 agents to 3 → **save 1-2 weeks in Phase 1**

---

### 6.3 Migration Path to Full Architecture

**Phase 1:** 3 agents (simplified)

**Phase 2:** Same (focus on frontend)

**Phase 3:** Optionally split Analysis Agent into CV Parser + Job Parser + Analyzer if:
- Performance profiling shows bottlenecks
- Need to optimize individual components
- Want to cache parsed CVs/jobs separately

**Recommendation: Start simple, add complexity when justified by data.**

**ACTION:** Update PRD Section 5.3 (Agent Architecture) with simplified 3-agent design for Phase 1, note potential expansion in Phase 3.

---

## 7. Data Model Assessment 📋

### 7.1 Proposed Models: GOOD FOUNDATION

**Strengths:**
- ✅ JSON schemas are clear and complete
- ✅ Include metadata (timestamps, IDs)
- ✅ Use UUID for IDs (good practice)
- ✅ ISO 8601 timestamps (good practice)

**Gaps & Recommendations:**

#### CV Document Schema

```json
{
  "id": "string (UUID)",
  "user_id": "string (optional, for Phase 3)",
  "content": "string (Markdown text)",
  "format": "markdown",
  "file_size": "integer (bytes)",
  "uploaded_at": "datetime (ISO 8601)",
  "metadata": {
    "original_filename": "string",
    "parsed_sections": ["skills", "experience", "education"]
  },
  
  // ADD THESE FIELDS:
  "ttl": "integer (seconds until auto-delete, for Cosmos DB TTL)",
  "version": "string (schema version, e.g., 'v1')",
  "hash": "string (SHA256 of content, for duplicate detection)"
}
```

**Rationale:**
- **ttl:** Enables automatic data deletion (see 3.2 Data Retention)
- **version:** Future-proofs schema evolution
- **hash:** Detect duplicate CV uploads (UX improvement)

---

#### Job Description Schema

```json
{
  "id": "string (UUID)",
  "content": "string (plain text)",
  "source_type": "manual | linkedin_url",
  "submitted_at": "datetime (ISO 8601)",
  "character_count": "integer",
  "parsed_data": {
    "title": "string",
    "required_skills": ["string"],
    "preferred_skills": ["string"],
    "experience_required": "string"
  },
  
  // ADD THESE FIELDS:
  "ttl": "integer",
  "version": "string",
  "hash": "string (for duplicate detection)"
}
```

**Same additions as CV for consistency.**

---

#### Analysis Document Schema

```json
{
  "id": "string (UUID)",
  "cv_id": "string (UUID reference)",
  "job_id": "string (UUID reference)",
  "overall_score": "integer (1-100)",
  "analyzed_at": "datetime (ISO 8601)",
  
  // ADD THESE FIELDS:
  "analysis_version": "string (which agent/prompt version used)",
  "processing_time_ms": "integer (for performance monitoring)",
  "token_usage": {
    "input_tokens": "integer",
    "output_tokens": "integer",
    "total_cost_usd": "float"
  },
  "status": "completed | failed | partial",
  "error": "string (if status=failed, error message)",
  "ttl": "integer",
  
  "analysis_results": { /* ... existing ... */ },
  "recommendations": { /* ... existing ... */ }
}
```

**Rationale:**
- **analysis_version:** Track which prompts/agents used (for A/B testing, debugging)
- **processing_time_ms:** Monitor performance
- **token_usage:** Cost tracking
- **status + error:** Handle failures gracefully
- **ttl:** Auto-deletion

**ACTION:** Update PRD Section 5.2 (Data Models) with additional fields listed above.

---

### 7.2 Cosmos DB Container Design

**Recommended Container Structure:**

```yaml
Container 1: "cvs"
  partition_key: /id
  indexing: default (all paths)
  TTL: enabled (delete after 30 days)
  
Container 2: "jobs"
  partition_key: /id
  indexing: default
  TTL: enabled (delete after 30 days)
  
Container 3: "analyses"
  partition_key: /cv_id  # Query by CV for history
  indexing: 
    - /cv_id (for queries)
    - /job_id (for queries)
    - /analyzed_at (for sorting)
  TTL: enabled (delete after 90 days)
```

**Rationale for `analyses` partition key:**
- Partition by `/cv_id` enables efficient "get all analyses for this CV" queries
- Acceptable since Phase 1 has no user auth (each CV is independent)
- Phase 3: May need to re-partition by `/user_id` (requires data migration)

**ACTION:** Document container design in PRD Section 5.2.

---

## 8. Recommended Simplifications 🎯

### 8.1 Simplify Agent Architecture (CRITICAL)

**Change:** 5 agents → 3 agents (see Section 6.2)

**Impact:**
- **Time saved:** 1-2 weeks in Phase 1
- **Complexity reduced:** Fewer moving parts
- **Performance improved:** Faster analysis (12s vs. 20s)
- **Cost reduced:** Fewer API calls, less prompt overhead

**Trade-off:** Less modular, but acceptable for MVP.

---

### 8.2 Remove Low-Priority Features from Phase 1

**Remove from Phase 1 P0/P1:**

1. **FR2.3 (Job Description Preprocessing):** Move to P2
   - AI handles messy text fine
   - Saves 2-3 days of work

2. **FR4.5 (Content to Remove):** Move to P2
   - Focus on positive recommendations first
   - Avoid demotivating users

3. **FR3.5 (Section-by-Section Analysis):** Move to P2
   - Nice-to-have but not critical
   - Overall score + recommendations are sufficient

**Time saved:** ~1 week

---

### 8.3 Use Cosmos DB Emulator for Development

**Change:** All local development uses Cosmos DB Emulator (not cloud instance)

**Benefits:**
- **Cost savings:** No RU charges during development
- **Faster iteration:** No network latency
- **Easier testing:** Reset data instantly

**Requirement:** Update setup docs to include emulator installation.

**ACTION:** Add to PRD Section 6 (Dependencies) and development setup instructions.

---

### 8.4 Defer "Nice-to-Have" Metrics

**Phase 1 Focus Metrics:**
- Analysis completion rate
- Average score
- Error rate

**Defer to Phase 2:**
- User satisfaction surveys (no UI yet)
- NPS (no user accounts)
- Recommendation implementation tracking (requires iteration)

**Rationale:** Focus on core technical metrics first, add business metrics when you have users.

---

## 9. Additional Recommendations 💡

### 9.1 Create Architecture Decision Records (ADRs)

**Required ADRs before Week 2:**

1. **ADR-001: Agent Framework Selection**
   - Which library? (semantic-kernel, autogen, custom)
   - Why?
   - Alternatives considered?

2. **ADR-002: Simplified 3-Agent Architecture**
   - Why merge parsers + analyzer?
   - Trade-offs accepted
   - Migration path to full architecture

3. **ADR-003: Cosmos DB Partition Strategy**
   - Why `/id` for Phase 1?
   - Migration plan for Phase 3 (if needed)

4. **ADR-004: Synchronous vs. Asynchronous Analysis**
   - Decision: Sync or async?
   - Timeout strategy
   - UX implications

5. **ADR-005: Prompt Engineering Approach**
   - Prompt storage strategy
   - Versioning
   - Testing methodology

**ACTION:** Create `docs/adr/` directory and template.

---

### 9.2 Add Healthcheck & Readiness Endpoints

**Missing from API spec:**

```yaml
GET /health
  Response: 200 OK
  {
    "status": "healthy",
    "checks": {
      "database": "ok",
      "ai_service": "ok"
    }
  }

GET /ready
  Response: 200 OK (if ready to serve traffic)
  Response: 503 Service Unavailable (if not ready)
```

**Rationale:** Required for Azure Container Apps health probes.

**ACTION:** Add to API endpoints section.

---

### 9.3 Implement Request Timeout Strategy

**Decision needed (Open Question #3):**

**Recommendation: Synchronous with 30s timeout**

**Rationale:**
- **Pros:** Simpler UX (wait for result, no polling)
- **Cons:** User waits up to 30s

**Alternative: Asynchronous (if >30s latency expected)**
- POST /analyses → 202 Accepted + analysis_id
- GET /analyses/{id} → poll until status=completed
- More complex but better for slow operations

**For Phase 1 with 3-agent architecture: Synchronous is fine** (estimated 12s).

**ACTION:** Make decision and update PRD Section 5.4 (API Design).

---

### 9.4 Add CI/CD Requirements

**Missing from PRD:**

```yaml
CI/CD Pipeline (GitHub Actions):

1. On Pull Request:
   - Run unit tests
   - Run linting (ruff, black)
   - Type checking (mypy)
   - Security scan (bandit)
   
2. On Merge to Main:
   - Run all tests (unit + integration)
   - Build Docker image
   - Push to Azure Container Registry
   - Deploy to staging environment
   
3. Manual Approval:
   - Deploy to production
   
4. Post-Deployment:
   - Run smoke tests
   - Monitor error rates for 10 minutes
   - Auto-rollback if error rate >5%
```

**ACTION:** Add Section 8.7 "CI/CD Requirements" to PRD.

---

## 10. Critical Action Items 🎯

### Before Development Starts (Week 1):

| Priority | Item | Owner | Deadline |
|----------|------|-------|----------|
| **P0** | Validate Microsoft Agent Framework availability and Python support | AI/ML Engineer | Day 2 |
| **P0** | Request Azure OpenAI quota increase (calculate token needs) | DevOps | Day 3 |
| **P0** | Decide on 3-agent vs. 5-agent architecture | Dev Lead + Team | Day 3 |
| **P0** | Create ADR-001 (Agent Framework), ADR-002 (Architecture) | Backend Dev | Day 5 |
| **P0** | Define Cosmos DB partition key strategy (ADR-003) | Backend Dev | Day 5 |
| **P0** | Add error handling specifications to PRD | Product + Dev Lead | Week 1 |
| **P1** | Research AG-UI framework maturity | Frontend Dev | Week 1 |
| **P1** | Add monitoring & observability requirements to PRD | DevOps + Dev Lead | Week 1 |
| **P1** | Define data retention policy (TTL values) | Product + Legal | Week 1 |
| **P1** | Calculate cost budget (OpenAI + Cosmos DB) | Product + DevOps | Week 1 |

---

### PRD Updates Required:

| Section | Change | Priority |
|---------|--------|----------|
| **Section 5.3** | Simplify to 3-agent architecture (or justify 5-agent) | P0 |
| **Section 5.2** | Add missing fields to data models (ttl, version, hash, etc.) | P0 |
| **Section 5.4** | Add API error responses, rate limiting, healthcheck | P0 |
| **Section 8** | Add new section: "Non-Functional Requirements" (logging, monitoring, security, performance, cost) | P0 |
| **Section 9** | Expand "Risks & Mitigation" with AI reliability risks | P1 |
| **Section 7** | Expand testing requirements (AI quality tests, golden set) | P1 |
| **Section 6** | Add Cosmos DB emulator to dependencies | P2 |
| **Section 5.4** | Decide and document sync vs. async analysis | P0 |

---

## 11. Final Verdict & Sign-Off 📝

### Overall Assessment

**Technical Feasibility: ✅ HIGH (8/10)**
- Stack is solid and proven
- Team can build this IF critical gaps are addressed
- Timeline is aggressive but achievable with simplifications

**Completeness: ⚠️ MODERATE (6/10)**
- Strong product foundation
- Missing critical technical details (error handling, monitoring, cost management)
- Needs ADRs for key decisions

**Complexity: ⚠️ HIGH FOR MVP**
- 5-agent architecture is over-engineered
- **Recommend 3-agent simplification** to reduce risk and timeline
- Phased approach is appropriate

**Risks: ⚠️ MODERATE**
- AI reliability risks (hallucination, inconsistency) need mitigation
- Performance risks manageable with 3-agent architecture
- Cost risks need budget definition

---

### Approval Status

✅ **APPROVED WITH CRITICAL MODIFICATIONS**

**Conditions:**
1. **MUST:** Address all P0 action items before development starts
2. **MUST:** Decide on 3-agent vs. 5-agent architecture (recommend 3-agent)
3. **MUST:** Update PRD with error handling, monitoring, and cost management sections
4. **SHOULD:** Create ADRs for key technical decisions
5. **SHOULD:** Validate AG-UI feasibility before committing to Phase 2 timeline

---

### Signature

**Reviewer:** Development Lead  
**Date:** December 31, 2025  
**Next Review:** After PRD v1.1 updates (estimated January 7, 2026)

---

## Appendix A: Simplified 3-Agent Architecture (Recommended)

```python
# Pseudo-code for simplified architecture

class AnalysisAgent:
    """
    Combines CV parsing, job parsing, and analysis into one AI call.
    """
    async def analyze(self, cv_content: str, job_content: str) -> AnalysisResult:
        prompt = f"""
        Analyze this CV against this job description.
        
        CV:
        {cv_content}
        
        Job Description:
        {job_content}
        
        Output JSON with:
        - parsed_cv (skills, experience, education)
        - parsed_job (requirements, responsibilities)
        - scores (overall, skills, experience, keywords)
        - gaps (missing skills, experience gaps)
        """
        
        response = await azure_openai.chat(prompt, response_format="json")
        return AnalysisResult.parse(response)

class ReportGeneratorAgent:
    """
    Generates actionable recommendations from analysis results.
    """
    async def generate(self, analysis: AnalysisResult) -> Report:
        prompt = f"""
        Given this analysis, generate specific recommendations.
        
        Analysis:
        {analysis.to_json()}
        
        Output JSON with:
        - summary (overall verdict, strengths, improvements)
        - recommendations (5-10 actionable items with priority)
        """
        
        response = await azure_openai.chat(prompt, response_format="json")
        return Report.parse(response)

class OrchestratorAgent:
    """
    Coordinates workflow.
    """
    async def run_analysis(self, cv_id: str, job_id: str) -> dict:
        # 1. Fetch CV and job from database
        cv = await db.get_cv(cv_id)
        job = await db.get_job(job_id)
        
        # 2. Run analysis (1 AI call)
        analysis = await AnalysisAgent().analyze(cv.content, job.content)
        
        # 3. Generate report (1 AI call)
        report = await ReportGeneratorAgent().generate(analysis)
        
        # 4. Save results
        analysis_doc = await db.save_analysis(cv_id, job_id, analysis, report)
        
        return analysis_doc
```

**Benefits:**
- **2 AI calls** instead of 4 (CV Parser + Job Parser + Analyzer + Report Generator)
- **~12 seconds** instead of 20-28 seconds
- **Simpler code**, fewer failure points
- **Lower cost** (less prompt overhead)

**Trade-off:**
- Less modular (but acceptable for MVP)
- Harder to cache parsed CVs/jobs separately (not needed in Phase 1)

---

## Appendix B: Cost Estimation

```yaml
Cost Calculation (Conservative Estimate):

Azure OpenAI (GPT-4o):
  - Analysis Agent: 5000 input + 2000 output = 7000 tokens
  - Report Generator: 2000 input + 1500 output = 3500 tokens
  - Total per analysis: 10,500 tokens
  - Cost: (7000 input * $5/1M) + (3500 output * $15/1M) = $0.035 + $0.0525 = $0.088/analysis
  - 10K analyses/day: $880/day = $26,400/month
  
Cosmos DB:
  - 3 containers, 1000 RU/s provisioned each = 3000 RU/s total
  - Cost: 3000 RU/s * $0.008/hour * 730 hours/month = ~$17,500/month
  - Note: Can optimize with autoscaling or serverless mode
  
Azure Container Apps:
  - 2 vCPU, 4GB RAM: ~$100/month
  
Total Monthly Cost (10K analyses/day):
  - ~$44,000/month
  
Optimization Opportunities:
  - Use Cosmos DB serverless (pay per operation): Reduce to ~$5K/month for low volume
  - Use Cosmos DB autoscale: Scale down during off-peak
  - Implement caching for repeated job descriptions: Save 20-30% on OpenAI costs
  
Recommended Phase 1 Budget: $5,000/month (assumes low volume, serverless Cosmos)
```

**ACTION:** Add to PRD Section 8.6 "Cost Management".

---

**END OF TECHNICAL REVIEW**
