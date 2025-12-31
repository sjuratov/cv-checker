# Product Requirements Document: CV Checker

**Version:** 1.0  
**Last Updated:** December 31, 2025  
**Status:** Draft  
**Owner:** Product Team

---

## Executive Summary

CV Checker is an AI-powered application that helps job seekers optimize their CVs by comparing them against specific job postings. The application provides a quantitative match score (1-100) and generates actionable recommendations to improve CV alignment with target roles.

The solution leverages Azure OpenAI (GPT-4o) for semantic analysis and is built using the Microsoft Agent Framework to orchestrate multiple specialized agents. This architecture ensures scalability, maintainability, and accurate analysis through domain-specific processing.

**Key Value Propositions:**
- **Objective Scoring:** Data-driven match assessment removes guesswork
- **Actionable Insights:** Specific recommendations on what to add, remove, or modify
- **Time Savings:** Automated analysis replaces manual CV tailoring
- **Career Advancement:** Increases interview opportunities through better CV-job alignment

---

## Project Overview

### Problem Statement
Job seekers struggle to tailor their CVs effectively for specific job postings. They often don't know:
- Which skills or experiences to emphasize
- What keywords are missing from their CV
- How well their background aligns with job requirements
- What specific changes would improve their chances

### Solution
CV Checker addresses these challenges by:
1. Accepting CV uploads (initially Markdown format)
2. Processing job descriptions (manual paste input)
3. Using AI to perform semantic matching and scoring
4. Generating detailed, actionable improvement recommendations

### Goals
- Enable job seekers to optimize CVs for specific roles in minutes
- Provide transparent, explainable scoring methodology
- Deliver concrete, implementable recommendations
- Support iterative CV improvement through analysis history

---

## User Personas

### Primary Persona: Active Job Seeker - "Sarah"
**Background:**
- 3-5 years professional experience in software development
- Applying to 10-15 jobs per week
- Has a general CV but knows it needs tailoring

**Goals:**
- Maximize interview callback rate
- Understand which jobs are best matches for her background
- Save time on manual CV customization

**Pain Points:**
- Unsure which skills to emphasize for different roles
- Doesn't know if her CV contains relevant keywords
- Lacks objective feedback on CV quality

**Usage Pattern:**
- Uploads CV once
- Tests against 5-10 different job postings per week
- Iterates CV based on recommendations
- Re-tests to validate improvements

### Secondary Persona: Career Coach - "Michael"
**Background:**
- Professional career counselor
- Works with 20-30 clients simultaneously
- Needs efficient tools to provide data-driven advice

**Goals:**
- Provide objective assessments to clients
- Demonstrate value through measurable improvements
- Scale coaching practice efficiently

**Pain Points:**
- Manual CV review is time-consuming
- Subjective assessments lack concrete metrics
- Difficult to track client progress over time

**Usage Pattern:**
- Uploads multiple client CVs
- Analyzes each against typical target roles
- Uses reports in coaching sessions
- Tracks improvement over multiple iterations

### Tertiary Persona: Internal Recruiter - "Jennifer"
**Background:**
- Recruiter at mid-sized tech company
- Reviews 50-100 CVs per week
- Wants to understand candidate fit quickly

**Goals:**
- Quickly assess candidate-role alignment
- Provide constructive feedback to promising candidates
- Reduce time-to-hire

**Pain Points:**
- Manual screening is subjective and time-intensive
- Difficult to explain rejection reasons objectively
- Miss qualified candidates due to keyword mismatches

**Usage Pattern:**
- Uploads candidate CVs in batches
- Runs against specific job requisitions
- Uses scores to prioritize candidate outreach
- Shares reports with hiring managers

---

## Features & Requirements

### Feature 1: CV Upload & Storage

**Description:** Users can upload their CV for analysis and storage.

**Requirements:**

**FR1.1** - CV File Upload
- **Priority:** P0 (Must Have)
- **Description:** System accepts Markdown (.md) format CVs via file upload
- **Acceptance Criteria:**
  - Upload endpoint accepts .md files up to 2MB
  - Validates file format and size
  - Returns upload confirmation with unique CV ID
  - Stores CV content in Azure Cosmos DB

**FR1.2** - CV Storage
- **Priority:** P0 (Must Have)
- **Description:** Store uploaded CVs for future analysis
- **Acceptance Criteria:**
  - Each CV assigned unique identifier
  - CV content stored in Azure Cosmos DB
  - Metadata captured: upload timestamp, file size, format
  - Supports retrieval by CV ID

**FR1.3** - CV Format Validation
- **Priority:** P0 (Must Have)
- **Description:** Validate CV content structure
- **Acceptance Criteria:**
  - Rejects files exceeding size limit
  - Validates Markdown syntax
  - Returns clear error messages for invalid formats
  - Logs validation failures

**FR1.4** - Multiple CV Management (Future)
- **Priority:** P2 (Nice to Have)
- **Description:** Users can manage multiple CV versions
- **Acceptance Criteria:**
  - Phase 3 implementation
  - Users can store multiple CVs
  - List and retrieve previous uploads

---

### Feature 2: Job Description Input

**Description:** Users provide job descriptions for comparison against their CV.

**Requirements:**

**FR2.1** - Manual Job Description Input
- **Priority:** P0 (Must Have)
- **Description:** Accept job descriptions via text paste
- **Acceptance Criteria:**
  - API endpoint accepts plain text job descriptions
  - Maximum length: 50,000 characters
  - Validates non-empty input
  - Returns job description ID upon successful submission

**FR2.2** - Job Description Storage
- **Priority:** P0 (Must Have)
- **Description:** Store job descriptions for analysis
- **Acceptance Criteria:**
  - Each job description assigned unique ID
  - Stored in Azure Cosmos DB
  - Metadata: submission timestamp, character count, source type
  - Retrievable by job ID

**FR2.3** - Job Description Preprocessing
- **Priority:** P1 (Should Have)
- **Description:** Clean and normalize job description text
- **Acceptance Criteria:**
  - Remove excessive whitespace
  - Standardize formatting
  - Extract key sections (responsibilities, requirements, nice-to-have)
  - Handle various input formats gracefully

**FR2.4** - LinkedIn URL Scraping (Future)
- **Priority:** P3 (Won't Have - Phase 3)
- **Description:** Extract job descriptions from LinkedIn URLs
- **Acceptance Criteria:**
  - Out of scope for Phase 1 & 2
  - Future enhancement for Phase 3

---

### Feature 3: CV-to-Job Analysis

**Description:** AI-powered semantic analysis comparing CV against job requirements.

**Requirements:**

**FR3.1** - Match Scoring
- **Priority:** P0 (Must Have)
- **Description:** Generate numerical match score (1-100)
- **Acceptance Criteria:**
  - Analyzes CV against job description using Azure OpenAI
  - Returns score on 1-100 scale
  - Score based on: skills match, experience relevance, keyword coverage
  - Consistent scoring methodology across analyses

**FR3.2** - Skills Gap Analysis
- **Priority:** P0 (Must Have)
- **Description:** Identify missing skills and experiences
- **Acceptance Criteria:**
  - Lists required skills not present in CV
  - Lists recommended skills not present in CV
  - Identifies experience gaps
  - Categorizes gaps by importance (critical, recommended, nice-to-have)

**FR3.3** - Keyword Matching
- **Priority:** P0 (Must Have)
- **Description:** Identify matching and missing keywords
- **Acceptance Criteria:**
  - Extracts keywords from job description
  - Identifies present keywords in CV
  - Lists missing critical keywords
  - Provides keyword density analysis

**FR3.4** - Experience Alignment
- **Priority:** P1 (Should Have)
- **Description:** Assess experience level match
- **Acceptance Criteria:**
  - Compares years of experience (if specified)
  - Analyzes seniority level alignment
  - Identifies overqualification or underqualification
  - Provides context-specific feedback

**FR3.5** - Section-by-Section Analysis
- **Priority:** P1 (Should Have)
- **Description:** Detailed analysis of CV sections
- **Acceptance Criteria:**
  - Analyzes: Skills, Experience, Education, Projects (if present)
  - Provides section-specific scores
  - Identifies strong and weak sections
  - Suggests section improvements

---

### Feature 4: Recommendation Report

**Description:** Generate comprehensive, actionable recommendations for CV improvement.

**Requirements:**

**FR4.1** - Overall Match Summary
- **Priority:** P0 (Must Have)
- **Description:** High-level summary of CV-job fit
- **Acceptance Criteria:**
  - Displays overall match score
  - Provides 2-3 sentence summary
  - Highlights top 3 strengths
  - Identifies top 3 improvement areas

**FR4.2** - Actionable Recommendations
- **Priority:** P0 (Must Have)
- **Description:** Specific, implementable CV improvements
- **Acceptance Criteria:**
  - Minimum 5 concrete recommendations
  - Categorized by: Add, Remove, Modify, Emphasize
  - Prioritized by impact (high, medium, low)
  - Each recommendation includes rationale

**FR4.3** - Skills to Add
- **Priority:** P0 (Must Have)
- **Description:** List missing skills that should be added
- **Acceptance Criteria:**
  - Identifies 3-10 missing skills
  - Explains why each skill matters
  - Categorizes as required vs. nice-to-have
  - Provides example phrasing

**FR4.4** - Content to Emphasize
- **Priority:** P0 (Must Have)
- **Description:** Highlight existing content to make more prominent
- **Acceptance Criteria:**
  - Identifies relevant but buried experience
  - Suggests specific sections to expand
  - Recommends keyword incorporation
  - Provides before/after examples

**FR4.5** - Content to Remove/De-emphasize
- **Priority:** P1 (Should Have)
- **Description:** Identify irrelevant or distracting content
- **Acceptance Criteria:**
  - Flags outdated or irrelevant experience
  - Identifies overly generic statements
  - Suggests condensing verbose sections
  - Explains impact on overall score

**FR4.6** - Keyword Optimization
- **Priority:** P1 (Should Have)
- **Description:** Specific keyword recommendations
- **Acceptance Criteria:**
  - Lists 5-15 missing critical keywords
  - Suggests natural integration points
  - Provides context for keyword usage
  - Warns against keyword stuffing

**FR4.7** - Report Export
- **Priority:** P2 (Nice to Have)
- **Description:** Export report in multiple formats
- **Acceptance Criteria:**
  - Phase 2/3 feature
  - Support JSON, PDF, Markdown export
  - Maintain formatting in all formats

---

### Feature 5: Analysis History

**Description:** Store and retrieve past analyses for tracking improvements.

**Requirements:**

**FR5.1** - Analysis Storage
- **Priority:** P1 (Should Have)
- **Description:** Store each analysis with full results
- **Acceptance Criteria:**
  - Each analysis saved to Azure Cosmos DB
  - Includes: CV ID, Job ID, score, recommendations, timestamp
  - Retrievable by analysis ID
  - Supports querying by CV ID or Job ID

**FR5.2** - History Retrieval
- **Priority:** P1 (Should Have)
- **Description:** Access previous analyses
- **Acceptance Criteria:**
  - API endpoint to list analyses by CV
  - Sort by date (newest first)
  - Filter by score range
  - Return paginated results

**FR5.3** - Progress Tracking (Future)
- **Priority:** P3 (Won't Have - Phase 3)
- **Description:** Visualize improvement over time
- **Acceptance Criteria:**
  - Phase 3 feature
  - Track score improvements across CV versions
  - Show recommendation implementation rate

---

## Technical Architecture

### Technology Stack

**Backend:**
- **Framework:** FastAPI (Python 3.11+)
- **Agent Framework:** Microsoft Agent Framework
- **AI Service:** Azure OpenAI (GPT-4o)
- **Database:** Azure Cosmos DB (NoSQL)
- **Hosting:** Azure App Service / Container Apps
- **API Design:** RESTful with OpenAPI documentation

**Frontend (Phase 2):**
- **Framework:** AG-UI
- **State Management:** TBD based on AG-UI requirements
- **API Client:** Auto-generated from OpenAPI spec

**DevOps:**
- **CI/CD:** GitHub Actions
- **Monitoring:** Azure Application Insights
- **Logging:** Structured logging with correlation IDs

### Data Models

**CV Document:**
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
  }
}
```

**Job Description Document:**
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
  }
}
```

**Analysis Document:**
```json
{
  "id": "string (UUID)",
  "cv_id": "string (UUID reference)",
  "job_id": "string (UUID reference)",
  "overall_score": "integer (1-100)",
  "analyzed_at": "datetime (ISO 8601)",
  "analysis_results": {
    "skills_match": {
      "score": "integer (1-100)",
      "matched_skills": ["string"],
      "missing_skills": ["string"]
    },
    "experience_match": {
      "score": "integer (1-100)",
      "relevant_experience": ["string"],
      "gaps": ["string"]
    },
    "keyword_analysis": {
      "score": "integer (1-100)",
      "matched_keywords": ["string"],
      "missing_keywords": ["string"]
    }
  },
  "recommendations": {
    "summary": "string",
    "strengths": ["string"],
    "improvements": ["string"],
    "actionable_items": [
      {
        "category": "add | remove | modify | emphasize",
        "priority": "high | medium | low",
        "description": "string",
        "rationale": "string"
      }
    ]
  }
}
```

---

## Agent Architecture (Microsoft Agent Framework)

### Agent Overview

The system employs five specialized agents coordinated through the Microsoft Agent Framework:

```
┌─────────────────────────────────────────────┐
│         Orchestrator Agent                  │
│  (Workflow coordination & state management) │
└────────────┬────────────────────────────────┘
             │
    ┌────────┼─────────┬─────────────┬─────────────┐
    │        │         │             │             │
    ▼        ▼         ▼             ▼             ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐ ┌──────────┐
│   CV   │ │ Job  │ │Analyzer│ │  Report  │ │ Storage  │
│ Parser │ │Parser│ │ Agent  │ │Generator │ │  Agent   │
└────────┘ └──────┘ └────────┘ └──────────┘ └──────────┘
```

### Agent Specifications

#### 1. Orchestrator Agent

**Responsibility:** Coordinate the entire CV analysis workflow.

**Capabilities:**
- Receive analysis requests (CV ID + Job ID)
- Orchestrate agent execution in correct sequence
- Manage state transitions
- Handle errors and retries
- Aggregate results from sub-agents
- Return final analysis to caller

**Workflow:**
1. Validate input (CV ID and Job ID exist)
2. Invoke CV Parser Agent → get structured CV data
3. Invoke Job Parser Agent → get structured job data
4. Invoke Analyzer Agent with both structured inputs → get scores and gaps
5. Invoke Report Generator Agent with analysis results → get recommendations
6. Invoke Storage Agent to persist analysis
7. Return complete analysis report

**Error Handling:**
- Retry transient failures (3 attempts)
- Fallback to partial results if non-critical agent fails
- Log all errors with correlation IDs
- Return user-friendly error messages

---

#### 2. CV Parser Agent

**Responsibility:** Extract and structure information from CV content.

**Capabilities:**
- Parse Markdown format CVs
- Extract sections: Skills, Experience, Education, Projects, Certifications
- Normalize skill names (e.g., "JS" → "JavaScript")
- Extract years of experience
- Identify education level and fields
- Handle various CV formats gracefully

**Input:**
- CV content (Markdown string)

**Output:**
```json
{
  "sections": {
    "skills": {
      "technical": ["Python", "FastAPI", "Azure"],
      "soft": ["Leadership", "Communication"]
    },
    "experience": [
      {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "duration": "2 years",
        "responsibilities": ["Built APIs", "Led team"],
        "technologies": ["Python", "PostgreSQL"]
      }
    ],
    "education": [
      {
        "degree": "B.S. Computer Science",
        "institution": "University",
        "year": "2020"
      }
    ],
    "certifications": ["AWS Certified"],
    "projects": [
      {
        "name": "Portfolio Website",
        "description": "Built with React",
        "technologies": ["React", "Node.js"]
      }
    ]
  },
  "metadata": {
    "total_experience_years": 3,
    "seniority_level": "mid"
  }
}
```

**AI Prompt Strategy:**
- Use Azure OpenAI with structured output (JSON mode)
- Provide CV parsing examples in system prompt
- Handle missing sections gracefully
- Extract implicit information (e.g., infer skills from project descriptions)

---

#### 3. Job Parser Agent

**Responsibility:** Extract and structure information from job descriptions.

**Capabilities:**
- Parse plain text job descriptions
- Extract job title, company, location
- Identify required vs. preferred qualifications
- Extract required skills and technologies
- Determine experience level requirements
- Identify education requirements
- Extract key responsibilities

**Input:**
- Job description content (plain text string)

**Output:**
```json
{
  "job_info": {
    "title": "Senior Software Engineer",
    "company": "Tech Startup",
    "location": "San Francisco, CA"
  },
  "requirements": {
    "required_skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
    "preferred_skills": ["Kubernetes", "React", "AWS"],
    "experience_level": "5+ years",
    "education": "Bachelor's degree in Computer Science or related field"
  },
  "responsibilities": [
    "Design and implement RESTful APIs",
    "Lead technical architecture decisions",
    "Mentor junior engineers"
  ],
  "nice_to_have": [
    "Experience with Azure",
    "Open source contributions"
  ]
}
```

**AI Prompt Strategy:**
- Use Azure OpenAI with structured output
- Classify skills by importance (required vs. preferred)
- Extract implicit requirements from responsibilities
- Normalize skill names for consistency

---

#### 4. Analyzer Agent

**Responsibility:** Perform semantic matching and scoring between CV and job.

**Capabilities:**
- Calculate overall match score (1-100)
- Generate sub-scores: skills match, experience match, keyword match
- Identify matched and missing skills
- Detect experience gaps
- Perform semantic similarity analysis (beyond keyword matching)
- Assess overqualification/underqualification

**Input:**
- Structured CV data (from CV Parser Agent)
- Structured job data (from Job Parser Agent)

**Output:**
```json
{
  "overall_score": 75,
  "subscores": {
    "skills_match": 80,
    "experience_match": 70,
    "keyword_match": 75,
    "education_match": 85
  },
  "skills_analysis": {
    "matched_required": ["Python", "FastAPI", "Docker"],
    "missing_required": ["PostgreSQL"],
    "matched_preferred": ["AWS"],
    "missing_preferred": ["Kubernetes", "React"]
  },
  "experience_analysis": {
    "years_match": "Candidate has 3 years, job requires 5+",
    "seniority_match": "Candidate is mid-level, job seeks senior",
    "relevant_experience": [
      "API development aligns with job responsibilities"
    ],
    "gaps": [
      "No leadership experience mentioned",
      "Limited mentoring experience"
    ]
  },
  "keyword_analysis": {
    "matched_keywords": ["API", "RESTful", "design"],
    "missing_keywords": ["architecture", "mentor", "lead"]
  }
}
```

**Scoring Methodology:**
- **Skills Match (30% weight):**
  - Required skills matched: +3 points each
  - Required skills missing: -3 points each
  - Preferred skills matched: +1 point each
  
- **Experience Match (30% weight):**
  - Years of experience alignment: 0-30 points
  - Relevant responsibilities: 0-20 points
  - Seniority level match: 0-10 points

- **Keyword Match (25% weight):**
  - Critical keywords present: +2 points each
  - Important keywords present: +1 point each

- **Education Match (15% weight):**
  - Meets requirements: 15 points
  - Exceeds requirements: 15 points
  - Below requirements: 0-10 points based on relevance

**AI Prompt Strategy:**
- Use Azure OpenAI for semantic understanding
- Go beyond literal keyword matching
- Consider synonyms and related concepts (e.g., "JavaScript" matches "JS")
- Assess context (e.g., "led team of 5" implies leadership)

---

#### 5. Report Generator Agent

**Responsibility:** Generate actionable, human-readable recommendations.

**Capabilities:**
- Create executive summary
- Generate prioritized recommendations
- Provide specific examples
- Categorize actions (Add, Remove, Modify, Emphasize)
- Explain rationale for each recommendation
- Maintain professional, encouraging tone

**Input:**
- Analysis results (from Analyzer Agent)
- Structured CV data
- Structured job data

**Output:**
```json
{
  "summary": {
    "overall_score": 75,
    "verdict": "Good match with room for improvement",
    "top_strengths": [
      "Strong Python and FastAPI skills match job requirements",
      "Relevant API development experience",
      "AWS certification aligns with preferred skills"
    ],
    "top_improvements": [
      "Add PostgreSQL experience to skills section",
      "Emphasize any leadership or mentoring activities",
      "Include 'architecture' and 'design patterns' keywords"
    ]
  },
  "recommendations": [
    {
      "id": 1,
      "category": "add",
      "priority": "high",
      "title": "Add PostgreSQL to Technical Skills",
      "description": "The job requires PostgreSQL experience, but it's not listed in your CV.",
      "rationale": "PostgreSQL is a required skill. If you have experience with it, add it prominently. If not, consider learning it or highlighting transferable database skills.",
      "example": "Add 'PostgreSQL' to your skills section, or mention a project where you used it.",
      "impact": "+5 points to overall score"
    },
    {
      "id": 2,
      "category": "emphasize",
      "priority": "high",
      "title": "Highlight Leadership Experience",
      "description": "The job seeks a senior engineer who can lead and mentor. Any leadership experience should be prominent.",
      "rationale": "Your CV mentions 'Led team' but doesn't elaborate. This is valuable for a senior role.",
      "example": "Expand: 'Led team of 3 engineers in developing microservices architecture, mentored 2 junior developers.'",
      "impact": "+4 points to experience match"
    },
    {
      "id": 3,
      "category": "modify",
      "priority": "medium",
      "title": "Incorporate 'Architecture' Terminology",
      "description": "Use keywords like 'architecture', 'design patterns', 'system design' in your experience descriptions.",
      "rationale": "These keywords appear multiple times in the job description and signal senior-level thinking.",
      "example": "Change 'Built APIs' to 'Designed and implemented RESTful API architecture using design patterns.'",
      "impact": "+3 points to keyword match"
    },
    {
      "id": 4,
      "category": "add",
      "priority": "medium",
      "title": "Add Kubernetes if Applicable",
      "description": "Kubernetes is listed as a preferred skill.",
      "rationale": "Preferred skills provide competitive advantage. If you have any K8s exposure, mention it.",
      "example": "Add 'Kubernetes' to skills or describe containerization/orchestration experience.",
      "impact": "+2 points to skills match"
    },
    {
      "id": 5,
      "category": "remove",
      "priority": "low",
      "title": "Consider Removing Outdated Technologies",
      "description": "If you have technologies that aren't relevant to this role, consider de-emphasizing them.",
      "rationale": "Irrelevant skills can dilute your CV's focus and confuse recruiters.",
      "example": "If you list 'PHP' but aren't applying for PHP roles, move it to a 'Additional Skills' section or remove it.",
      "impact": "+1 point to overall clarity"
    }
  ],
  "next_steps": [
    "Revise your CV based on high-priority recommendations",
    "Re-run the analysis to see improved score",
    "Consider obtaining PostgreSQL certification if you lack hands-on experience",
    "Prepare interview examples that demonstrate leadership and mentoring"
  ]
}
```

**AI Prompt Strategy:**
- Use Azure OpenAI for natural language generation
- Maintain encouraging, constructive tone
- Provide concrete examples, not generic advice
- Prioritize recommendations by impact
- Limit to 5-10 actionable items (avoid overwhelming users)

---

### Agent Communication

**Framework:** Microsoft Agent Framework handles:
- Message passing between agents
- State management across agent executions
- Error propagation and handling
- Logging and observability
- Agent lifecycle management

**Message Format (Internal):**
```json
{
  "correlation_id": "string (UUID)",
  "source_agent": "string (agent name)",
  "target_agent": "string (agent name)",
  "message_type": "request | response | error",
  "timestamp": "datetime (ISO 8601)",
  "payload": {
    "data": "object (agent-specific)"
  }
}
```

---

## API Design

### Core Endpoints

#### Upload CV
```
POST /api/v1/cvs
Content-Type: multipart/form-data

Request:
- file: CV file (Markdown)

Response: 201 Created
{
  "cv_id": "uuid",
  "uploaded_at": "datetime",
  "format": "markdown",
  "file_size": 1024
}
```

#### Submit Job Description
```
POST /api/v1/jobs
Content-Type: application/json

Request:
{
  "content": "string (job description text)",
  "source_type": "manual"
}

Response: 201 Created
{
  "job_id": "uuid",
  "submitted_at": "datetime",
  "character_count": 2048
}
```

#### Analyze CV Against Job
```
POST /api/v1/analyses
Content-Type: application/json

Request:
{
  "cv_id": "uuid",
  "job_id": "uuid"
}

Response: 202 Accepted (for async processing)
{
  "analysis_id": "uuid",
  "status": "processing",
  "estimated_completion": "datetime"
}

OR

Response: 200 OK (for sync processing)
{
  "analysis_id": "uuid",
  "overall_score": 75,
  "summary": {...},
  "recommendations": [...]
}
```

#### Get Analysis Results
```
GET /api/v1/analyses/{analysis_id}

Response: 200 OK
{
  "analysis_id": "uuid",
  "cv_id": "uuid",
  "job_id": "uuid",
  "overall_score": 75,
  "analyzed_at": "datetime",
  "subscores": {...},
  "summary": {...},
  "recommendations": [...]
}
```

#### List Analyses for CV
```
GET /api/v1/cvs/{cv_id}/analyses?limit=10&offset=0

Response: 200 OK
{
  "cv_id": "uuid",
  "total_count": 23,
  "analyses": [
    {
      "analysis_id": "uuid",
      "job_id": "uuid",
      "overall_score": 75,
      "analyzed_at": "datetime"
    }
  ]
}
```

---

## Success Metrics

### Business Metrics

1. **User Engagement**
   - Target: 70% of users who upload a CV complete at least one analysis
   - Target: 40% of users perform 3+ analyses within first month
   - Measurement: Track analysis completion rate, repeat usage

2. **User Satisfaction**
   - Target: Net Promoter Score (NPS) ≥ 40
   - Target: 75% of users rate recommendations as "helpful" or "very helpful"
   - Measurement: Post-analysis surveys, feedback forms

3. **Utility & Impact**
   - Target: 60% of users report implementing at least 3 recommendations
   - Target: 50% of users report improved CV-job scores after revisions
   - Measurement: Follow-up surveys, score improvement tracking

### Technical Metrics

1. **Performance**
   - Target: 95% of analyses complete within 30 seconds
   - Target: API response time p95 < 500ms for non-analysis endpoints
   - Target: 99.9% uptime
   - Measurement: Application Insights, Azure Monitor

2. **Accuracy**
   - Target: 85% agreement between CV Checker scores and human recruiter assessments (±10 points)
   - Target: 90% of recommendations deemed "relevant" by users
   - Measurement: A/B testing against recruiter reviews, user feedback

3. **Reliability**
   - Target: <1% error rate on analyses
   - Target: Successful agent orchestration in 99% of requests
   - Target: Data consistency across all Azure Cosmos DB operations
   - Measurement: Error logs, agent execution telemetry

4. **Scalability**
   - Target: Support 100 concurrent analyses
   - Target: Handle 10,000 analyses per day
   - Target: Agent processing time scales linearly with load
   - Measurement: Load testing, performance benchmarks

---

## Acceptance Criteria

### Phase 1: Backend MVP (Weeks 1-6)

**AC1.1 - CV Upload & Storage**
- [ ] User can upload Markdown CV via API
- [ ] CV stored in Azure Cosmos DB with unique ID
- [ ] CV retrievable by ID
- [ ] API returns appropriate errors for invalid files

**AC1.2 - Job Description Input**
- [ ] User can submit job description text via API
- [ ] Job description stored with unique ID
- [ ] Content validation (max length, non-empty)
- [ ] Job retrievable by ID

**AC1.3 - Agent Framework Implementation**
- [ ] Orchestrator Agent successfully coordinates workflow
- [ ] CV Parser Agent extracts skills, experience, education
- [ ] Job Parser Agent extracts requirements and responsibilities
- [ ] Analyzer Agent generates scores (overall + subscores)
- [ ] Report Generator Agent produces recommendations
- [ ] All agents communicate via Microsoft Agent Framework

**AC1.4 - Analysis Execution**
- [ ] User can trigger analysis with CV ID + Job ID
- [ ] Analysis completes within 30 seconds for typical inputs
- [ ] Returns overall score (1-100)
- [ ] Returns minimum 5 actionable recommendations
- [ ] Analysis stored in Azure Cosmos DB

**AC1.5 - Azure OpenAI Integration**
- [ ] Agents use GPT-4o for semantic analysis
- [ ] Structured output (JSON mode) validated
- [ ] Error handling for API failures (retries, fallbacks)
- [ ] Token usage optimized (cost-efficient prompts)

**AC1.6 - API Documentation**
- [ ] OpenAPI specification auto-generated
- [ ] All endpoints documented with examples
- [ ] Error responses documented
- [ ] Swagger UI available for testing

**AC1.7 - Testing**
- [ ] Unit tests for each agent (80% code coverage)
- [ ] Integration tests for agent orchestration
- [ ] End-to-end API tests
- [ ] Load testing (100 concurrent requests)

---

### Phase 2: Frontend & UX (Weeks 7-10)

**AC2.1 - AG-UI Integration**
- [ ] Frontend scaffolding with AG-UI
- [ ] CV upload interface
- [ ] Job description input interface
- [ ] Analysis results display
- [ ] Responsive design (mobile, tablet, desktop)

**AC2.2 - User Experience**
- [ ] Upload CV: <3 clicks to complete
- [ ] Submit job description: paste and submit in <2 clicks
- [ ] View results: clear score visualization + recommendations
- [ ] Loading states for async operations
- [ ] Error messages user-friendly and actionable

**AC2.3 - Results Visualization**
- [ ] Overall score prominently displayed (gauge/progress bar)
- [ ] Subscores broken down (skills, experience, keywords)
- [ ] Recommendations grouped by category (Add, Modify, etc.)
- [ ] Priority indicators (high, medium, low)
- [ ] Expandable recommendation details

**AC2.4 - Analysis History**
- [ ] List previous analyses for a CV
- [ ] View past analysis details
- [ ] Compare scores across analyses
- [ ] Sort/filter by date or score

**AC2.5 - Usability Testing**
- [ ] 5+ users complete full workflow without assistance
- [ ] Task success rate >90% (upload, analyze, review)
- [ ] Average time to first analysis <5 minutes
- [ ] User satisfaction survey score ≥4/5

---

### Phase 3: Advanced Features (Future)

**AC3.1 - Multi-Format Support**
- [ ] PDF CV upload and parsing
- [ ] DOCX CV upload and parsing
- [ ] Format auto-detection
- [ ] Consistent parsing quality across formats

**AC3.2 - LinkedIn Integration**
- [ ] Accept LinkedIn job URLs
- [ ] Scrape job description content
- [ ] Handle LinkedIn anti-scraping measures
- [ ] Fallback to manual input if scraping fails

**AC3.3 - User Authentication**
- [ ] User registration and login
- [ ] CV management per user account
- [ ] Analysis history per user
- [ ] Secure credential storage

**AC3.4 - Advanced Analytics**
- [ ] Track CV score improvements over time
- [ ] Benchmark scores against similar roles
- [ ] Recommendation implementation tracking
- [ ] Success metrics (interviews, offers)

**AC3.5 - Export & Sharing**
- [ ] Export analysis as PDF
- [ ] Export as JSON for programmatic use
- [ ] Share analysis via unique URL
- [ ] Print-friendly report format

---

## Out of Scope

The following features are explicitly **NOT included** in the initial product:

### Phase 1 & 2 Exclusions

1. **User Authentication & Accounts**
   - No user registration or login
   - No user profiles or saved preferences
   - No multi-user isolation (anonymous usage only)

2. **Payment & Monetization**
   - No subscription plans
   - No pay-per-analysis
   - No freemium model

3. **Multi-Format CV Support**
   - No PDF parsing (Phase 1 & 2)
   - No DOCX parsing (Phase 1 & 2)
   - Markdown only initially

4. **Job Description Scraping**
   - No LinkedIn URL scraping (Phase 1 & 2)
   - No Indeed, Glassdoor, or other site scraping
   - Manual paste only initially

5. **CV Generation/Editing**
   - No in-app CV editor
   - No CV template generation
   - No automated CV rewriting (recommendations only)

6. **Advanced Analytics**
   - No industry benchmarking
   - No comparison against other candidates
   - No predictive "interview probability" scores

7. **Collaboration Features**
   - No sharing analyses with others
   - No comments or feedback on analyses
   - No coach/client relationship management

8. **Integrations**
   - No applicant tracking system (ATS) integration
   - No calendar integration
   - No email notifications
   - No Slack/Teams bots

9. **Mobile Apps**
   - No native iOS app
   - No native Android app
   - Web-only (responsive design in Phase 2)

10. **Offline Mode**
    - No offline analysis capability
    - Requires internet connection for all operations

---

### Future Consideration (Phase 3+)

These features may be considered after Phase 2 based on user feedback and business priorities:

- Multi-language support (non-English CVs and jobs)
- Cover letter analysis and generation
- Interview preparation based on CV-job gaps
- Company culture fit analysis
- Salary expectation recommendations
- Browser extension for one-click analysis on job sites
- API access for third-party integrations
- White-label solution for recruitment agencies

---

## Phased Rollout Plan

### Phase 1: Backend MVP (Weeks 1-6)
**Goal:** Build functional backend with agent framework and analysis capabilities.

**Deliverables:**
- FastAPI backend with all core endpoints
- Microsoft Agent Framework integration
- Five specialized agents (Orchestrator, CV Parser, Job Parser, Analyzer, Report Generator)
- Azure OpenAI integration (GPT-4o)
- Azure Cosmos DB setup and data models
- API documentation (OpenAPI)
- Unit, integration, and load tests

**Success Criteria:**
- All Phase 1 acceptance criteria met
- End-to-end analysis works via API
- Performance targets met (30s analysis time)
- 80% code coverage

**Risks:**
- Azure OpenAI rate limits or quota issues
- Agent orchestration complexity
- Cosmos DB partitioning strategy

**Mitigation:**
- Request increased OpenAI quotas early
- Start with simple agent workflows, iterate
- Design flexible partition key strategy

---

### Phase 2: Frontend & User Experience (Weeks 7-10)
**Goal:** Build user-facing interface with AG-UI for seamless interaction.

**Deliverables:**
- AG-UI frontend application
- CV upload interface
- Job description input interface
- Analysis results visualization
- Analysis history view
- Responsive design
- End-to-end user testing

**Success Criteria:**
- All Phase 2 acceptance criteria met
- Usability testing with 5+ users (>90% task success)
- Average time to first analysis <5 minutes
- Mobile-responsive design

**Risks:**
- AG-UI learning curve
- Frontend-backend integration issues
- Performance on slow connections

**Mitigation:**
- Allocate time for AG-UI exploration
- Use OpenAPI auto-generated client
- Optimize API responses (minimize payload size)

---

### Phase 3: Advanced Features (Future)
**Goal:** Expand format support, add authentication, and enhance features based on user feedback.

**Deliverables:**
- PDF and DOCX CV parsing
- LinkedIn URL scraping
- User authentication and accounts
- Advanced analytics (progress tracking)
- Export features (PDF, JSON)

**Success Criteria:**
- User retention increases by 25%
- Multi-format parsing accuracy >90%
- Authentication implemented securely

**Timing:**
- TBD based on Phase 2 learnings and user demand

---

## Dependencies

### External Dependencies

1. **Azure Services**
   - Azure OpenAI (GPT-4o access)
   - Azure Cosmos DB instance
   - Azure App Service / Container Apps
   - Azure Application Insights

2. **Microsoft Agent Framework**
   - Framework library availability
   - Documentation and examples
   - Community support

3. **AG-UI Framework** (Phase 2)
   - Framework maturity
   - Documentation
   - Component library

### Internal Dependencies

1. **Azure Account & Permissions**
   - Azure subscription with sufficient credits
   - Permissions to create resources
   - OpenAI service access granted

2. **Development Team**
   - Backend developer (Python, FastAPI)
   - AI/ML engineer (prompt engineering, agents)
   - Frontend developer (AG-UI) - Phase 2
   - DevOps engineer (Azure deployment)

3. **Design & UX** (Phase 2)
   - UI/UX designer for AG-UI screens
   - User researcher for testing

---

## Risks & Mitigation

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Azure OpenAI rate limits | High | Medium | Request quota increase; implement retry logic; cache results |
| Agent framework complexity | Medium | Medium | Start simple; incremental complexity; thorough testing |
| Cosmos DB partitioning issues | Medium | Low | Design flexible schema; test at scale early; consult Azure experts |
| CV parsing accuracy (varied formats) | High | Medium | Start with Markdown only; expand formats in Phase 3; validate with real CVs |
| Analysis quality (inaccurate scores) | High | Medium | Validate against recruiter assessments; iteratively refine prompts; A/B test |

### Business Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Low user adoption | High | Medium | Beta testing with target users; iterate based on feedback; marketing strategy |
| Users disagree with scores | Medium | High | Provide transparent scoring methodology; allow feedback; continuous improvement |
| Competitors with better features | Medium | Medium | Focus on accuracy and UX; differentiate with agent architecture; rapid iteration |
| Privacy concerns (CV data) | High | Low | Transparent data policies; minimal data retention; encryption at rest/transit |

### Legal/Compliance Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data privacy regulations (GDPR, CCPA) | High | Low | Anonymize data in Phase 1; implement data deletion; legal review before Phase 3 auth |
| AI bias in scoring | Medium | Medium | Regular bias audits; diverse training examples; human validation |
| Copyright (job descriptions) | Low | Low | User-submitted content; terms of service clarity; no redistribution |

---

## Open Questions

1. **Azure OpenAI Quota:** What is the initial GPT-4o token quota? Do we need to request an increase?
   - **Owner:** DevOps Engineer
   - **Deadline:** Week 1

2. **Microsoft Agent Framework:** Which version/library should we use? Are there code examples for our use case?
   - **Owner:** AI/ML Engineer
   - **Deadline:** Week 1

3. **Analysis Processing:** Should analysis be synchronous or asynchronous? (Trade-off: UX vs. scalability)
   - **Owner:** Backend Developer + Product
   - **Deadline:** Week 2

4. **Data Retention:** How long should we keep CVs, jobs, and analyses? (Anonymous in Phase 1)
   - **Owner:** Product + Legal
   - **Deadline:** Week 2

5. **Cosmos DB Partition Key:** What should we use for partition key? (CV ID, user ID in future, or composite?)
   - **Owner:** Backend Developer
   - **Deadline:** Week 2

6. **Scoring Transparency:** Should we show detailed scoring breakdown to users, or just overall score?
   - **Owner:** Product + UX (Phase 2)
   - **Deadline:** Week 6 (before Phase 2)

7. **Beta Testing:** Who are our initial beta users? How do we recruit them?
   - **Owner:** Product + Marketing
   - **Deadline:** Week 4

---

## Appendix

### Glossary

- **CV (Curriculum Vitae):** Document summarizing professional experience, skills, and education
- **Job Description:** Text describing a job opening, including requirements and responsibilities
- **Match Score:** Numerical rating (1-100) indicating CV-job alignment
- **Agent:** Autonomous software component with specific responsibility in the system
- **Orchestrator:** Agent that coordinates other agents' execution
- **Semantic Analysis:** AI-powered understanding of meaning beyond keyword matching
- **Actionable Recommendation:** Specific, implementable suggestion for CV improvement

### References

- [Microsoft Agent Framework Documentation](https://docs.microsoft.com/azure/agent-framework)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure Cosmos DB Best Practices](https://learn.microsoft.com/azure/cosmos-db/best-practices)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AG-UI Framework](https://github.com/microsoft/ag-ui) (TBD - Phase 2)

### Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-31 | Product Team | Initial PRD creation |

---

**End of Document**
