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
- Browses LinkedIn for relevant job postings
- Copies LinkedIn job URLs (5-10 per week) and pastes into CV Checker
- Reviews analysis results and recommendations
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

## Data Persistence & Storage

### Business Value

Data persistence transforms CV Checker from a stateless tool into a valuable career companion. By storing CVs, job descriptions, and analysis results, users gain:

- **Historical Context:** Track improvements over time, compare different CV versions, understand which changes increased match scores
- **Returning User Experience:** No need to re-upload CVs or re-enter job descriptions on subsequent visits
- **Data Continuity:** Analysis history provides evidence of CV optimization efforts, useful for career coaching and job search tracking
- **Future Extensibility:** Foundation for advanced features like progress dashboards, multi-device sync, and data export

### Core Entities to Persist

**1. CVs (Curriculum Vitae)**
- User-uploaded CV content (Markdown format)
- Upload metadata: timestamp, filename, file size
- Association with user session/account

**2. Jobs (Job Descriptions)**
- Manually entered or scraped job description text
- Source information: manual vs LinkedIn URL
- Submission timestamp and character count

**3. Analysis Results**
- Complete analysis output: scores, recommendations, matched/missing skills
- References to associated CV and Job
- Analysis timestamp for historical tracking
- Enables re-viewing past analyses without re-processing

### User Identification Strategy (MVP)

Phase 2 introduces **session-based user identification** without authentication:

- **Frontend generates UUID** on first visit, stored in browser localStorage
- **User ID serves as partition key** in Azure Cosmos DB (efficient data isolation)
- **No login required:** Users access their data via persistent session ID
- **Browser-specific:** Data accessible only from the browser where analysis was performed
- **Privacy-friendly:** No email, password, or personal information collected

**Limitations (Addressed in Phase 3 with Authentication):**
- Data not accessible across devices or browsers
- Clearing browser data loses session ID (data orphaned)
- No password protection on analysis history

**User Experience:**
- Seamless: No registration friction for first-time users
- Transparent: Privacy notice explains local session storage
- Optional: "Clear My Data" button removes all stored analyses

### Local vs Azure Deployment

**Local Development: Docker Compose + Cosmos DB Linux Emulator**
- **No Azure account required** for local development
- **Full feature parity** with production environment
- **Fast iteration:** No network latency, instant restarts
- **Cost-free:** Emulator runs locally, no Azure charges
- **Setup:** Single `docker-compose up` command starts backend + Cosmos DB emulator

**Production: Azure Cosmos DB**
- **Serverless tier (recommended for MVP):** Pay only for operations performed, auto-scales
- **Single container:** `cv-checker-data` with `userId` partition key
- **Global distribution:** Low-latency reads/writes from any region (future)
- **Automatic indexing:** Efficient queries on `userId`, `createdAt`, `type` fields
- **Seamless migration:** Local development data schema matches production exactly

**Deployment Strategy:**
- **Environment variable swap:** Backend reads connection string from `COSMOS_CONNECTION_STRING` environment variable
- **Local:** Points to Cosmos DB emulator (`https://localhost:8081/`)
- **Production:** Points to Azure Cosmos DB account
- **No code changes** required when moving from local to cloud

### Data Retention & Privacy

**MVP (Phase 2):**
- **No automatic deletion:** Data persists until user manually clears session or browser data
- **No cross-user access:** userId ensures data isolation
- **No data export:** Users can view but not download analysis history (Phase 3 feature)

**Future (Phase 3 with Authentication):**
- **GDPR compliance:** User-initiated data deletion, data export ("Download My Data")
- **Retention policy:** Option to auto-delete analyses older than X months
- **Multi-device sync:** Authenticated users access data from any device

---

## Features & Requirements

### Feature 1: CV Upload & Storage

**Description:** Users can upload their CV for analysis and storage.

**Requirements:**

**FR1.1** - CV File Upload
- **Priority:** P0 (Must Have)
- **Description:** System accepts Markdown (.md) format CVs via frontend file upload
- **Acceptance Criteria:**
  - Frontend accepts .md files up to 2MB
  - Validates file format and size client-side
  - CV content sent to backend as part of analysis request
  - Backend stores CV content in Azure Cosmos DB with unique ID
  - CV associated with userId from frontend session

**FR1.2** - CV Storage
- **Priority:** P0 (Must Have)
- **Description:** Store uploaded CVs for future analysis and retrieval
- **Acceptance Criteria:**
  - Each CV assigned unique identifier (UUID)
  - CV content stored in Azure Cosmos DB
  - Metadata captured: userId, upload timestamp, filename, file size, format
  - Supports retrieval by CV ID and userId (partition key)
  - CVs accessible only by originating userId (data isolation)

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
- **Description:** Store job descriptions for analysis and historical reference
- **Acceptance Criteria:**
  - Each job description assigned unique ID (UUID)
  - Stored in Azure Cosmos DB with userId partition key
  - Metadata: userId, submission timestamp, character count, source type (manual/LinkedIn URL)
  - Retrievable by job ID and userId
  - Jobs accessible only by originating userId

**FR2.3** - Job Description Preprocessing & Validation
- **Priority:** P1 (Should Have)
- **Description:** Clean, normalize, and validate job description text
- **Acceptance Criteria:**
  - Remove excessive whitespace
  - Standardize formatting
  - Extract key sections (responsibilities, requirements, nice-to-have)
  - Handle various input formats gracefully
  - Validate minimum content length (50 characters for manual input)
  - For LinkedIn-scraped content: accept any length >0, log warning if <50
  - Reject empty or whitespace-only content with clear error message

**FR2.4** - LinkedIn URL Fetching
- **Priority:** P1 (Should Have - Phase 2)
- **Description:** Extract job descriptions from LinkedIn job posting URLs
- **Acceptance Criteria:**
  - Backend endpoint accepts LinkedIn job URLs
  - Server-side scraping using Playwright (headless browser)
  - Returns raw job description text content
  - Validates LinkedIn URL format before attempting fetch
  - Handles errors gracefully: invalid URLs, network timeouts, blocked requests
  - No structured data extraction in scraper (Job Parser Agent handles that)
  - Returns appropriate error messages for scraping failures

**FR2.5** - Dual Input Mode UI
- **Priority:** P1 (Should Have - Phase 2)
- **Description:** Allow users to toggle between LinkedIn URL and manual text input
- **Acceptance Criteria:**
  - Toggle control to switch between "LinkedIn URL" and "Manual Input" modes
  - In LinkedIn URL mode: single text input for URL with "Fetch" action
  - In Manual Input mode: textarea for job description (existing functionality)
  - Auto-populate job description field once LinkedIn content is fetched
  - Clear visual feedback during fetch operation (loading state)
  - Error display for failed fetch attempts with actionable guidance
  - Seamless fallback to manual input if fetch fails

---

### Feature 2B: LinkedIn Job URL Fetching (Phase 2)

**Description:** Automated extraction of job descriptions from LinkedIn URLs to streamline job input.

**User Story:**
> As a job seeker, I want to paste a LinkedIn job URL instead of manually copying the entire job description, so that I can quickly analyze multiple jobs without tedious copy-paste work.

**Requirements:**

**FR2B.1** - LinkedIn URL Validation
- **Priority:** P1 (Should Have - Phase 2)
- **Description:** Validate LinkedIn URLs before fetching
- **Acceptance Criteria:**
  - Accept URLs matching pattern: `https://www.linkedin.com/jobs/view/*` or `https://linkedin.com/jobs/view/*`
  - Reject non-LinkedIn URLs with clear error message
  - Handle URL variations (with/without www, trailing slashes, query parameters)
  - Return validation errors before attempting fetch

**FR2B.2** - Server-Side Web Scraping
- **Priority:** P1 (Should Have - Phase 2)
- **Description:** Use Playwright to scrape LinkedIn job content
- **Acceptance Criteria:**
  - Run Playwright in headless mode on backend
  - Navigate to LinkedIn job URL
  - Extract raw job description text (no HTML parsing in scraper)
  - Accept any content length >0 characters
  - Log warning if content <50 characters (unusually short)
  - Timeout after 15 seconds with appropriate error
  - Return plain text content for Job Parser Agent to process
  - Rate limit: 5 requests/minute per IP, 20 requests/hour per IP (Phase 2 - no user authentication)

**FR2B.3** - Error Handling & Fallback
- **Priority:** P1 (Should Have - Phase 2)
- **Description:** Graceful degradation when LinkedIn fetch fails
- **Acceptance Criteria:**
  - Handle network timeouts (15s max)
  - Handle LinkedIn anti-scraping blocks (CAPTCHA, rate limits)
  - Handle invalid/deleted job postings (404)
  - Return user-friendly error messages
  - Suggest manual input as fallback
  - Log failure reasons for monitoring

**FR2B.4** - Separation of Concerns
- **Priority:** P1 (Should Have - Phase 2)
- **Description:** Scraper only retrieves raw text; structured extraction handled by Job Parser Agent
- **Acceptance Criteria:**
  - Scraper returns unstructured job description text
  - No extraction of job title, skills, requirements in scraper
  - Job Parser Agent receives same input format as manual text
  - Consistent downstream processing regardless of input source

**Technical Design Notes:**

**Why Playwright?**
- Handles JavaScript-rendered content (LinkedIn is a SPA)
- Stealth mode reduces detection by anti-scraping systems
- Headless browser ensures accurate rendering
- Cross-platform support (dev, staging, prod)

**Deployment Considerations:**
- Azure Container Apps recommended (supports headless browsers)
- Alternative: Azure App Service with custom Docker image including Playwright
- Resource requirements: ~512MB RAM per concurrent scraping operation
- Consider rate limiting to avoid LinkedIn blocks (max 10 requests/minute)

**Error Scenarios:**
1. **Invalid URL:** Immediate validation error, no fetch attempted
2. **Network Timeout:** Retry once, then return timeout error
3. **LinkedIn Block:** Return blocked error, suggest manual input
4. **Job Not Found (404):** Return not found error, suggest checking URL
5. **Content Extraction Failed:** Return generic error, suggest manual input

**Privacy & Legal:**
- User provides URL; we fetch publicly accessible content
- No LinkedIn authentication required (public job postings only)
- Scraped content stored same as manual input (per data retention policy)
- Terms of Service should clarify user responsibility for URL legality

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

### Feature 4B: Tabbed Analysis Report Interface

**Description:** Redesign the analysis results page with a 3-tab interface for better organization and readability, allowing users to view their CV, job description, and analysis results in separate, focused tabs.

**Priority:** P0 (Must Have) - UI/UX Enhancement

**User Stories:**

1. As a job seeker, I want to view my CV alongside the analysis results so I can quickly reference what I submitted without scrolling through a long page.
2. As a job seeker, I want to view the job description alongside recommendations so I can understand the context and verify the AI's interpretation.
3. As a job seeker, I want organized tabs so I can focus on one aspect at a time (my CV, the job, or the results) without information overload.
4. As a job seeker using mobile, I want tabs that work well on small screens so I can review my analysis anywhere.

**Requirements:**

**FR4B.1** - Three-Tab Interface
- **Priority:** P0 (Must Have)
- **Description:** Implement a tabbed interface with three distinct tabs for analysis page
- **Acceptance Criteria:**
  - Three clearly labeled tabs: "CV Document", "Job Description", "Analysis Results"
  - Only one tab active/visible at a time
  - Smooth transitions between tabs (no page reload)
  - Tabs accessible via click/tap
  - Clear visual indication of active tab (highlighting, underline, or similar)
  - Inactive tabs clearly distinguishable from active tab
  - Tab labels concise and descriptive

**FR4B.2** - CV Document Tab
- **Priority:** P0 (Must Have)
- **Description:** Display uploaded CV in rendered Markdown format
- **Acceptance Criteria:**
  - CV content rendered as formatted Markdown (headers, lists, bold, italic, links)
  - Markdown rendering is XSS-safe (sanitized)
  - Maintains original CV structure and formatting
  - Readable typography (appropriate font size, line height, spacing)
  - Independent scroll context (scrolling in CV tab doesn't affect other tabs)
  - Displays full CV content (no truncation)
  - Handles empty or missing CV gracefully (shows placeholder message)

**FR4B.3** - Job Description Tab
- **Priority:** P0 (Must Have)
- **Description:** Display job description in rendered Markdown format
- **Acceptance Criteria:**
  - Job description rendered as formatted Markdown
  - Markdown rendering is XSS-safe (sanitized)
  - Maintains job description structure and formatting
  - Readable typography matching CV tab style for consistency
  - Independent scroll context
  - Displays full job description (no truncation)
  - Shows source indicator (manual input vs LinkedIn URL) if applicable
  - Handles empty or missing job description gracefully

**FR4B.4** - Analysis Results Tab
- **Priority:** P0 (Must Have)
- **Description:** Display comprehensive analysis results in organized layout
- **Acceptance Criteria:**
  - Contains all existing analysis components:
    - Overall match score with visual gauge/progress indicator
    - Subscores breakdown (skills match, experience match, keyword match, education match)
    - Top strengths (3-5 items)
    - Top improvement areas (3-5 items)
    - Detailed actionable recommendations (categorized by Add, Remove, Modify, Emphasize)
    - Priority indicators (high, medium, low) for recommendations
  - Independent scroll context
  - Organized sections with clear headings
  - Visual hierarchy for scannability
  - Maintains all existing functionality from single-page view

**FR4B.5** - Default Tab & State Persistence
- **Priority:** P0 (Must Have)
- **Description:** Smart default tab selection and session persistence
- **Acceptance Criteria:**
  - "Analysis Results" tab is active by default on first page load
  - Active tab selection persists during browser session (survives page refresh)
  - Tab state stored in browser's sessionStorage
  - Returns to last viewed tab when navigating back to analysis page
  - Session state cleared when starting new analysis
  - Does not persist across browser sessions (privacy consideration)

**FR4B.6** - Responsive Tab Design
- **Priority:** P0 (Must Have)
- **Description:** Tabs work seamlessly across all device sizes
- **Acceptance Criteria:**
  - Desktop (≥1024px): Full-width tabs, side-by-side layout
  - Tablet (768-1023px): Full-width tabs, may stack or remain horizontal
  - Mobile (≤767px): Horizontal scrollable tabs if needed, or stacked tabs
  - Touch-friendly tap targets (minimum 44×44px per accessibility guidelines)
  - No horizontal overflow on small screens (tabs don't break layout)
  - Tab labels remain readable on all screen sizes (may abbreviate if needed)
  - Smooth scroll behavior for tab content on all devices

**FR4B.7** - Accessibility & Keyboard Navigation
- **Priority:** P1 (Should Have)
- **Description:** Ensure tabs are accessible to all users
- **Acceptance Criteria:**
  - Keyboard navigation: Tab key moves focus between tabs
  - Enter/Space key activates focused tab
  - ARIA labels for screen readers (`role="tablist"`, `role="tab"`, `role="tabpanel"`)
  - Active tab indicated in ARIA state (`aria-selected="true"`)
  - Focus indicator visible for keyboard users
  - Skip-to-content link available if tabs are at top of page
  - Color contrast meets WCAG AA standards (4.5:1 for text)

**FR4B.8** - Markdown Rendering Security
- **Priority:** P0 (Must Have)
- **Description:** Safely render user-submitted content to prevent XSS attacks
- **Acceptance Criteria:**
  - Use XSS-safe Markdown library (e.g., `marked` with DOMPurify, or `react-markdown`)
  - Sanitize all HTML output before rendering
  - Disable dangerous Markdown features (raw HTML injection, JavaScript links)
  - Allow safe Markdown: headers, lists, bold, italic, links (http/https only), code blocks
  - Test with XSS attack vectors (e.g., `<script>alert('XSS')</script>`, `javascript:` links)
  - No script execution in rendered content
  - Security review of Markdown rendering implementation

**FR4B.9** - Tab Content Styling
- **Priority:** P1 (Should Have)
- **Description:** Consistent, professional styling across all tabs
- **Acceptance Criteria:**
  - CV and Job Description tabs use same Markdown styles (headings, lists, spacing)
  - Analysis Results tab maintains existing design system
  - Adequate padding/margins in all tabs for readability
  - Background colors differentiate tabs if needed (subtle)
  - Print-friendly styles (optional: print each tab separately)
  - Dark mode support if application supports dark mode

**Success Metrics:**

1. **User Engagement:**
   - 80%+ of users interact with at least 2 tabs per analysis session
   - Average time on analysis page increases by 20% (indicates thorough review)
   - Tab switch rate: Users switch tabs 3-5 times per session (exploring content)

2. **User Satisfaction:**
   - User survey: 85%+ rate tabbed interface as "helpful" or "very helpful"
   - User survey: 75%+ prefer tabbed interface over single-page scrolling view
   - Reduced bounce rate on analysis results page (users spend more time reviewing)

3. **Usability:**
   - 95%+ of users can successfully navigate between tabs without guidance
   - Zero reported XSS vulnerabilities in Markdown rendering
   - Mobile usability score ≥4.5/5 for tabbed interface

4. **Performance:**
   - Tab switching response time <100ms (instant feel)
   - Markdown rendering completes within 200ms for typical CV/job content
   - No performance degradation on low-end mobile devices

**Technical Considerations:**

1. **Frontend Framework:**
   - Use native browser tab component if AG-UI provides one
   - Fallback to custom tab implementation with accessible ARIA attributes
   - Component state management (active tab, content loading states)

2. **Markdown Rendering:**
   - Library recommendation: `react-markdown` (if using React) or `marked` + `DOMPurify` (vanilla JS)
   - Configure to disable HTML injection: `disallowedElements: ['script', 'iframe', 'object', 'embed']`
   - Allow safe elements only: headings, paragraphs, lists, links, code, emphasis
   - Apply CSS classes for consistent styling

3. **State Management:**
   - Store active tab index in `sessionStorage` as `activeAnalysisTab`
   - Retrieve on component mount, default to "Analysis Results" (index 2) if not set
   - Clear on new analysis submission
   - Consider URL hash for deep linking (e.g., `#tab=cv-document`) in future iteration

4. **Performance Optimization:**
   - Lazy render tab content (render only active tab initially, render others on first view)
   - Cache rendered Markdown to avoid re-rendering on tab switch
   - Virtual scrolling for very long CVs/jobs (optional, for performance)

5. **API Considerations:**
   - **Architectural Decision:** CV markdown content and job description text are stored in CosmosDB along with analysis results
   - **Data Consistency:** This ensures that current runs and historical analyses have the same data structure
   - API returns the following fields with analysis results:
     - `cv_markdown`: Full CV content (stored with analysis)
     - `job_description`: Full job description text (stored with analysis)
     - `source_type`: "manual" or "linkedin_url" (stored with analysis)
     - `source_url`: LinkedIn URL if applicable (stored with analysis)
   - **Benefits:**
     - Enables users to view what CV and job they analyzed in the past
     - Ensures data completeness for historical analyses
     - Simplifies frontend implementation (single data source)
     - No separate API calls needed for each tab
     - Supports future features like data export and multi-device access

6. **Browser Compatibility:**
   - Test on Chrome, Firefox, Safari, Edge (latest versions)
   - Test on iOS Safari and Chrome (mobile)
   - Test on Android Chrome (mobile)
   - Polyfills for `sessionStorage` if needed (rare)

**Implementation Phases:**

**Phase 2.1: Basic Tab Structure (Week 7)**
- Implement 3-tab UI component
- Wire up tab switching logic
- Add sessionStorage persistence
- Basic responsive layout

**Phase 2.2: Content Rendering (Week 8)**
- Integrate Markdown rendering library
- Implement XSS sanitization
- Style CV and Job Description tabs
- Test with sample content

**Phase 2.3: Analysis Results Tab (Week 8-9)**
- Migrate existing analysis results UI to tab
- Ensure all components render correctly in tab context
- Adjust styling for tab container

**Phase 2.4: Polish & Accessibility (Week 9)**
- Add keyboard navigation
- Implement ARIA attributes
- Responsive design testing (mobile, tablet, desktop)
- Cross-browser testing

**Phase 2.5: Testing & QA (Week 10)**
- Security testing (XSS attack vectors)
- Performance testing (large CVs/jobs)
- Usability testing with real users
- Bug fixes and refinements

**Risks & Mitigation:**

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Markdown rendering XSS vulnerability | High | Low | Use battle-tested library (DOMPurify); security review; penetration testing |
| Performance issues with large documents | Medium | Medium | Implement lazy rendering; virtual scrolling; optimize Markdown parser |
| Tab navigation confusing for users | Medium | Low | User testing early; clear visual indicators; tooltips if needed |
| Mobile tap targets too small | Medium | Low | Follow accessibility guidelines (44×44px); test on real devices |
| State persistence conflicts | Low | Low | Use sessionStorage (isolated per tab); clear on new analysis |

**Open Questions:**

1. **Tab Order:** Should we allow users to reorder tabs, or is fixed order (CV, Job, Results) sufficient?
   - **Recommendation:** Fixed order for MVP; allow customization in Phase 3 if requested
   - **Owner:** Product + UX

2. **Tab Icons:** Should tabs have icons in addition to labels? (e.g., 📄 CV Document, 📋 Job Description, 📊 Analysis Results)
   - **Recommendation:** Text-only for MVP; icons add visual clutter on mobile
   - **Owner:** UX Designer

3. **Print Functionality:** Should users be able to print each tab separately, or entire analysis?
   - **Recommendation:** Print entire analysis (all tabs) for MVP; separate tab printing in Phase 3
   - **Owner:** Product

4. **Deep Linking:** Should tabs be accessible via URL hash (e.g., `/analysis/123#job-description`)?
   - **Recommendation:** Not in Phase 2; add in Phase 3 if users share specific tabs
   - **Owner:** Backend Developer + Product

---

### Feature 5: Analysis History

**Description:** Store and retrieve past analyses for tracking improvements.

**Requirements:**

**FR5.1** - Analysis Storage
- **Priority:** P0 (Must Have - Phase 2)
- **Description:** Store each analysis with full results for historical tracking
- **Acceptance Criteria:**
  - Each analysis saved to Azure Cosmos DB with userId partition key
  - Includes: userId, CV ID, Job ID, overall score, subscores, recommendations, timestamp
  - Retrievable by analysis ID and userId
  - Supports querying by userId to list all user analyses
  - Data isolation: analyses accessible only by originating userId

**FR5.2** - History Retrieval
- **Priority:** P0 (Must Have - Phase 2)
- **Description:** Access previous analyses by user session
- **Acceptance Criteria:**
  - API endpoint to list analyses by userId
  - Sort by date (newest first) or score (highest/lowest first)
  - Filter by date range, score range
  - Return paginated results (10 per page default)
  - Include CV filename and job title/preview for context

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
- **Web Scraping:** Playwright (headless browser) - Phase 2
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
  "source_url": "string (optional, LinkedIn URL if applicable)",
  "submitted_at": "datetime (ISO 8601)",
  "character_count": "integer",
  "fetch_status": "success | failed | not_applicable",
  "fetch_error": "string (optional, error message if fetch failed)",
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
  "user_id": "string (session UUID)",
  "cv_id": "string (UUID reference)",  // DEPRECATED - keeping for backward compatibility
  "job_id": "string (UUID reference)",  // DEPRECATED - keeping for backward compatibility
  "cv_markdown": "string (full CV content)",  // NEW - stored with analysis for historical consistency
  "job_description": "string (full job text)",  // NEW - stored with analysis for historical consistency
  "source_type": "manual | linkedin_url",  // NEW - job input method
  "source_url": "string (optional, LinkedIn URL)",  // NEW - if source_type is linkedin_url
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

**Rationale for Storing CV and Job Content with Analysis:**
- **Data Completeness:** Ensures historical analyses are self-contained with all necessary context
- **User Experience:** Enables users to view what CV and job description they analyzed in the past without referencing separate documents
- **Simplified Frontend:** Single API call returns all data needed for the 3-tab interface (CV, Job, Results)
- **Future-Proof:** Supports data export, multi-device access, and archival features
- **Consistency:** Current and historical analyses have identical data structure

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

Request (Manual Input):
{
  "source_type": "manual",
  "content": "string (job description text)"
}

Request (LinkedIn URL):
{
  "source_type": "linkedin_url",
  "url": "string (LinkedIn job posting URL)"
}

Response: 201 Created (Manual Input)
{
  "job_id": "uuid",
  "submitted_at": "datetime",
  "content": "string (job description)",
  "character_count": 2048,
  "source_type": "manual",
  "fetch_status": "not_applicable"
}

Response: 200 OK (LinkedIn URL - Success)
{
  "job_id": "uuid",
  "submitted_at": "datetime",
  "content": "string (scraped job description)",
  "character_count": 1543,
  "source_type": "linkedin_url",
  "source_url": "https://linkedin.com/jobs/view/123",
  "fetch_status": "success"
}

Response: 400 Bad Request (LinkedIn fetch failed)
{
  "success": false,
  "error": "failed_to_fetch",
  "message": "Unable to fetch content from LinkedIn URL",
  "details": "Request timeout after 15 seconds",
  "fallback": "manual_input"
}

Response: 400 Bad Request (Invalid content)
{
  "success": false,
  "error": "invalid_content",
  "message": "Job description is too short (minimum 50 characters required)",
  "details": "Received 23 characters"
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
  "cv_markdown": "string (full CV content)",  // NEW - enables CV tab display
  "job_description": "string (full job text)",  // NEW - enables Job Description tab display
  "source_type": "manual | linkedin_url",  // NEW - indicates job input method
  "source_url": "string (optional)",  // NEW - LinkedIn URL if applicable
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
  "cv_id": "uuid",  // DEPRECATED - keeping for backward compatibility
  "job_id": "uuid",  // DEPRECATED - keeping for backward compatibility
  "cv_markdown": "string (full CV content)",  // NEW - for CV tab display
  "job_description": "string (full job text)",  // NEW - for Job Description tab display
  "source_type": "manual | linkedin_url",  // NEW - job input method
  "source_url": "string (optional)",  // NEW - LinkedIn URL if applicable
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
   - Target: 50% of job inputs use LinkedIn URL mode (Phase 2)
   - Measurement: Track analysis completion rate, repeat usage, input mode preferences

2. **User Satisfaction**
   - Target: Net Promoter Score (NPS) ≥ 40
   - Target: 75% of users rate recommendations as "helpful" or "very helpful"
   - Target: 80% of users find LinkedIn URL fetching "convenient" or "very convenient" (Phase 2)
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
   - Target: ≥90% success rate for LinkedIn URL fetching (Phase 2)
   - Target: LinkedIn fetch operations complete within 15 seconds (Phase 2)
   - Measurement: Error logs, agent execution telemetry, scraping success rates

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

**AC2.4 - LinkedIn URL Fetching**
- [ ] Backend endpoint accepts LinkedIn job URLs
- [ ] Playwright successfully scrapes LinkedIn job descriptions
- [ ] Fetch completes within 15 seconds for 90% of requests
- [ ] Error handling for invalid URLs, timeouts, and blocked requests
- [ ] Scraped content automatically passed to Job Parser Agent
- [ ] No structured parsing in scraper (separation of concerns maintained)

**AC2.5 - Dual Input Mode UI**
- [ ] Toggle control switches between "LinkedIn URL" and "Manual Input" modes
- [ ] LinkedIn URL mode: text input + fetch button
- [ ] Manual Input mode: textarea (existing functionality)
- [ ] Loading indicator during fetch operation
- [ ] Auto-populate job description after successful fetch
- [ ] Clear error messages with fallback guidance
- [ ] Seamless mode switching without data loss

**AC2.6 - Analysis History**
- [ ] List previous analyses for a CV
- [ ] View past analysis details
- [ ] Compare scores across analyses
- [ ] Sort/filter by date or score
- [ ] Display source type (manual vs LinkedIn URL) for each job

**AC2.7 - Usability Testing**
- [ ] 5+ users complete full workflow without assistance
- [ ] Task success rate >90% (upload, analyze, review)
- [ ] Average time to first analysis <5 minutes
- [ ] LinkedIn URL fetch success rate >85% in user testing
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

4. **Job Description Scraping (Phase 1 Only)**
   - No LinkedIn URL scraping in Phase 1 (added in Phase 2)
   - No Indeed, Glassdoor, or other site scraping (Phase 1 & 2)
   - Manual paste only in Phase 1

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
- Browser extension for one-click analysis on job sites (LinkedIn + other boards)
- API access for third-party integrations
- White-label solution for recruitment agencies
- Additional job board URL fetching (Indeed, Glassdoor, etc.)

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
**Goal:** Build user-facing interface with AG-UI for seamless interaction, including LinkedIn URL fetching.

**Deliverables:**
- AG-UI frontend application
- CV upload interface
- Dual-mode job input interface (LinkedIn URL + Manual)
- LinkedIn URL fetching backend service (Playwright)
- Analysis results visualization
- Analysis history view
- Responsive design
- End-to-end user testing

**Success Criteria:**
- All Phase 2 acceptance criteria met
- Usability testing with 5+ users (>90% task success)
- Average time to first analysis <5 minutes
- LinkedIn URL fetch success rate >90%
- Mobile-responsive design

**Risks:**
- AG-UI learning curve
- Frontend-backend integration issues
- Performance on slow connections
- LinkedIn anti-scraping measures blocking requests
- Playwright deployment complexity in Azure

**Mitigation:**
- Allocate time for AG-UI exploration
- Use OpenAPI auto-generated client
- Optimize API responses (minimize payload size)
- Implement robust error handling and fallback to manual input
- Test Playwright in Azure environment early; use browser-in-container approach

---

### Phase 3: Advanced Features (Future)
**Goal:** Expand format support, add authentication, and enhance features based on user feedback.

**Deliverables:**
- PDF and DOCX CV parsing
- User authentication and accounts
- Advanced analytics (progress tracking)
- Export features (PDF, JSON)
- Additional job board integrations (Indeed, Glassdoor)

**Success Criteria:**
- User retention increases by 25%
- Multi-format parsing accuracy >90%
- Authentication implemented securely
- Support for 3+ job board sources

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
| LinkedIn anti-scraping blocks requests | Medium | High | Implement retry logic; headless browser with stealth mode; fallback to manual input; monitor success rates |

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

8. **Playwright Deployment:** What's the best approach for deploying Playwright in Azure? (Container Apps vs App Service with custom runtime)
   - **Owner:** DevOps Engineer
   - **Deadline:** Week 6 (before Phase 2)

9. **LinkedIn Scraping Reliability:** What's acceptable success rate for LinkedIn fetching? Should we implement rate limiting?
   - **Owner:** Backend Developer + Product
   - **Deadline:** Week 7

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
