# Feature Requirements Document: AG-UI Frontend

**Version:** 1.1  
**Last Updated:** December 31, 2025  
**Status:** Technical Review Complete  
**Phase:** Phase 2 - Frontend Implementation  
**Owner:** Frontend Team  
**Technical Reviewer:** Developer Lead  
**Related Documents:** [PRD](../prd.md), [ADR-005](../adr/ADR-005-fastapi-backend-architecture.md), [Backend README](../../backend/README.md)

---

## 🚨 Critical Technical Notes (Developer Lead Review)

### Backend Integration Requirements
1. **API Endpoint:** The backend has a **single stateless endpoint** `POST /api/v1/analyze` - NOT separate CV/job/analysis endpoints
2. **No Backend Storage:** All analysis history must be managed in **frontend localStorage** (per ADR-004)
3. **Recommendations are Strings:** Phase 1 backend returns `recommendations: string[]` - NOT structured objects. Frontend must handle gracefully.
4. **Response Schema:** Use `backend/app/models/responses.py` as source of truth for TypeScript type generation

### AG-UI Framework Validation Required
⚠️ **CRITICAL:** AG-UI framework availability and documentation must be verified before Phase 2 kickoff.
- **If AG-UI not available:** Fall back to **Fluent UI 2** (Microsoft design system) or **React + Radix UI**
- **Action Item:** Product/Engineering to confirm AG-UI readiness by Week 6

### Security Priorities
1. **File Upload Validation:** Client-side checks for file type, size, content (prevent XSS)
2. **Input Sanitization:** Strip control characters, normalize whitespace, no HTML rendering
3. **CSP Headers:** Configure Content Security Policy in Azure Static Web Apps
4. **Dependency Security:** `npm audit` in CI/CD, fail on critical vulnerabilities

### Performance Requirements
- **Page Load:** First Contentful Paint <1.5s, Time to Interactive <3s
- **API Timeout:** 60s for analysis (backend can take 20-30s), 10s for other endpoints
- **Lighthouse CI:** Enforce scores >90 (Performance), >95 (Accessibility) in CI/CD

### Testing Coverage
- **Unit Tests:** >80% coverage for utilities, state management, API client
- **Integration Tests:** Full workflows (upload → analyze → results)
- **E2E Tests:** Playwright/Cypress against staging environment
- **Accessibility Tests:** axe-core in CI/CD, manual NVDA/VoiceOver testing

---

## Table of Contents
1. [Feature Overview](#feature-overview)
2. [User Stories](#user-stories)
3. [Functional Requirements](#functional-requirements)
4. [UI/UX Requirements](#uiux-requirements)
5. [Technical Requirements](#technical-requirements)
6. [Acceptance Criteria](#acceptance-criteria)
7. [Out of Scope](#out-of-scope)
8. [Success Metrics](#success-metrics)

---

## Feature Overview

### Purpose
Build a user-facing web interface using the AG-UI framework that enables job seekers, career coaches, and recruiters to analyze CV-to-job match quality through an intuitive, accessible, and responsive interface.

### Goals
- Enable users to complete their first CV analysis within 5 minutes
- Provide clear, actionable visualization of analysis results
- Support seamless interaction with backend API built in Phase 1
- Deliver responsive experience across mobile, tablet, and desktop devices
- Maintain WCAG 2.1 AA accessibility standards

### Key Value Propositions
- **Simplicity:** Upload CV and paste job description in <5 clicks
- **Clarity:** Visual score display with color-coded recommendations
- **Actionability:** Prioritized, categorized recommendations for immediate implementation
- **Transparency:** Clear breakdown of subscores and scoring methodology
- **Continuity:** Access to analysis history for tracking improvements

### Technology Foundation
- **Framework:** AG-UI (Microsoft's agent-optimized UI framework)
- **API Integration:** Auto-generated client from OpenAPI specification
- **State Management:** AG-UI recommended patterns
- **Styling:** AG-UI component library and theme system
- **Deployment:** Azure Static Web Apps

---

## User Stories

### Primary Persona: Sarah - Active Job Seeker

#### User Story 1: First-Time Analysis
**As** Sarah, a job seeker,  
**I want to** upload my CV and paste a job description to get a match score,  
**So that** I can understand how well my CV aligns with a specific job posting.

**Acceptance Criteria:**
- Upload CV via file picker or drag-and-drop
- Paste job description into textarea
- Click "Analyze Match" button
- See loading indicator during processing
- View overall match score (1-100) displayed prominently
- See prioritized list of recommendations
- Complete workflow in under 5 minutes

**Priority:** P0 (Must Have)

---

#### User Story 2: Understanding My Score
**As** Sarah,  
**I want to** see a detailed breakdown of my match score,  
**So that** I can understand which areas of my CV are strong and which need improvement.

**Acceptance Criteria:**
- Overall score displayed with visual indicator (gauge/progress bar)
- Subscores shown for: Skills Match, Experience Match, Keyword Match, Education Match
- Each subscore has explanation tooltip
- Color-coded scoring (red <50, yellow 50-74, green 75+)
- Summary statement interpreting the overall score

**Priority:** P0 (Must Have)

---

#### User Story 3: Implementing Recommendations
**As** Sarah,  
**I want to** see actionable, prioritized recommendations,  
**So that** I know exactly what to change in my CV to improve my score.

**Acceptance Criteria:**
- Recommendations categorized by type (Add, Remove, Modify, Emphasize)
- Each recommendation shows priority (High, Medium, Low)
- Recommendations include rationale and example
- High-priority recommendations appear first
- Each recommendation expandable for details
- Minimum 5 recommendations per analysis

**Priority:** P0 (Must Have)

---

#### User Story 4: Tracking Improvements
**As** Sarah,  
**I want to** view my previous analyses,  
**So that** I can track my CV improvements over time and compare scores.

**Acceptance Criteria:**
- Access "Analysis History" from main interface
- List of past analyses with dates and scores
- Sort by date (newest first) or score (highest first)
- Click on past analysis to view full details
- Visual indicator of score improvement/decline
- Paginated results (10 per page)

**Priority:** P1 (Should Have)

---

### Secondary Persona: Michael - Career Coach

#### User Story 5: Efficient Client Assessment
**As** Michael, a career coach,  
**I want to** quickly upload multiple client CVs and analyze them against target roles,  
**So that** I can provide data-driven coaching advice efficiently.

**Acceptance Criteria:**
- Upload different CVs for different clients
- Save/bookmark frequently used job descriptions
- Access analysis results quickly
- Clear labeling of which CV was analyzed
- Export or print analysis results for client meetings

**Priority:** P2 (Nice to Have - Phase 3)

---

#### User Story 6: Demonstrating Value
**As** Michael,  
**I want to** show clients visual progress over time,  
**So that** I can demonstrate the value of my coaching services.

**Acceptance Criteria:**
- Compare multiple analyses side-by-side
- Show score improvement graph
- Highlight implemented recommendations
- Export comparison reports

**Priority:** P3 (Won't Have - Phase 3)

---

### Tertiary Persona: Jennifer - Recruiter

#### User Story 7: Quick Candidate Screening
**As** Jennifer, an internal recruiter,  
**I want to** quickly assess candidate-role fit,  
**So that** I can prioritize outreach to best-matched candidates.

**Acceptance Criteria:**
- Upload candidate CV quickly
- Analyze against job requisition
- See overall score within 30 seconds
- Identify top 3 strengths and gaps immediately
- Share results with hiring manager

**Priority:** P2 (Nice to Have - Phase 2/3)

---

## Functional Requirements

### FR-FE1: CV Upload Interface

#### FR-FE1.1: File Selection Methods
**Description:** Provide multiple intuitive ways to upload CV files.

**Requirements:**
- **File Picker Button:** Styled primary button labeled "Upload CV" or "Choose File"
- **Drag-and-Drop Zone:** Designated area with visual affordance (dashed border, upload icon)
- **Visual Feedback:** Highlight drop zone when file is dragged over
- **File Validation:** Client-side validation before upload
  - Accepted formats: `.md` (Markdown)
  - Maximum file size: 2MB
  - Display clear error for invalid format or oversized file

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  📄 Upload Your CV                      │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │   Drag & drop your CV here       │  │
│  │   or                              │  │
│  │   [Choose File]                   │  │
│  │                                   │  │
│  │   Accepted: Markdown (.md)       │  │
│  │   Max size: 2MB                   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Error States:**
- "Invalid file format. Please upload a Markdown (.md) file."
- "File too large. Maximum size is 2MB."
- "Failed to upload file. Please try again."

**Success State:**
- "✓ CV uploaded successfully: [filename.md]"
- Display file name, size, and upload timestamp
- Option to "Remove" and upload different file

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1, AC2.2

---

#### FR-FE1.2: Upload Progress Indicator
**Description:** Show upload progress for larger files.

**Requirements:**
- Progress bar (0-100%) during upload
- Cancel upload option
- Estimated time remaining for uploads >500KB
- Success confirmation upon completion
- Automatic transition to next step

**Priority:** P1 (Should Have)

---

### FR-FE2: Job Description Input

#### FR-FE2.1: Textarea Input
**Description:** Provide intuitive input area for job description text.

**Requirements:**
- **Textarea Component:** Multi-line text input, minimum 10 rows
- **Character Counter:** Real-time count display (current / 50,000 max)
- **Placeholder Text:** Helpful prompt (e.g., "Paste the job description here...")
- **Auto-resize:** Textarea expands as user types (up to max height)
- **Clear Button:** Quick way to clear entire input
- **Validation:** Client-side validation before submission
  - Minimum 100 characters
  - Maximum 50,000 characters
  - Non-empty requirement

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  📋 Job Description                     │
│  ┌───────────────────────────────────┐  │
│  │ Paste the job description here... │  │
│  │                                   │  │
│  │                                   │  │
│  │                                   │  │
│  │                                   │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│  Characters: 0 / 50,000        [Clear]  │
└─────────────────────────────────────────┘
```

**Validation Messages:**
- "Job description is required."
- "Job description must be at least 100 characters."
- "Job description exceeds maximum length (50,000 characters)."

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1, AC2.2

---

#### FR-FE2.2: Format Preservation
**Description:** Preserve formatting from pasted content.

**Requirements:**
- Maintain line breaks from pasted content
- Remove excessive whitespace (normalize)
- Visual preview of formatted text
- Toggle between "Edit" and "Preview" modes

**Priority:** P1 (Should Have)

---

### FR-FE3: Analysis Trigger & Processing

#### FR-FE3.1: Analysis Initiation
**Description:** Enable users to start analysis with clear call-to-action.

**Requirements:**
- **Analyze Button:** Primary action button labeled "Analyze Match"
- **Button State Management:**
  - Disabled when CV not uploaded or job description empty
  - Enabled when both inputs valid
  - Loading state during processing (spinner + text)
- **Validation Check:** Final validation before API call
- **Error Prevention:** Clear messaging if prerequisites not met

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  [Analyze Match]                        │
│                                         │
│  ✓ CV uploaded                          │
│  ✓ Job description provided             │
└─────────────────────────────────────────┘

(Loading State)
┌─────────────────────────────────────────┐
│  [⟳ Analyzing... Please wait]           │
│                                         │
│  Our AI is comparing your CV against   │
│  the job description. This usually      │
│  takes 20-30 seconds.                   │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1, AC2.2

---

#### FR-FE3.2: Loading States
**Description:** Provide clear feedback during async analysis processing.

**Requirements:**
- **Progress Indicator:** Spinner or progress bar
- **Status Messages:** Dynamic updates (e.g., "Parsing CV...", "Analyzing skills match...", "Generating recommendations...")
- **Estimated Time:** "Usually completes in 20-30 seconds"
- **Cancel Option:** Ability to cancel analysis in progress
- **Timeout Handling:** Show error if analysis takes >60 seconds
- **Accessibility:** Loading states announced to screen readers

**Loading States Sequence:**
1. "Starting analysis..." (0-5s)
2. "Parsing your CV..." (5-10s)
3. "Analyzing job requirements..." (10-15s)
4. "Calculating match score..." (15-25s)
5. "Generating recommendations..." (25-30s)
6. "Analysis complete!" (transition to results)

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.2

---

#### FR-FE3.3: Error Handling
**Description:** Gracefully handle analysis failures with actionable messages.

**Requirements:**
- **API Error Handling:** Catch and display user-friendly messages
- **Network Errors:** "Unable to connect. Please check your internet connection."
- **Server Errors:** "Analysis failed. Please try again in a few moments."
- **Timeout Errors:** "Analysis is taking longer than expected. Please try again."
- **Retry Mechanism:** "Retry Analysis" button
- **Error Details (Optional):** Collapsible technical details for debugging
- **Support Link:** Link to help documentation or support contact

**Error UI:**
```
┌─────────────────────────────────────────┐
│  ⚠️ Analysis Failed                     │
│                                         │
│  We couldn't complete the analysis.     │
│  This might be due to high server load. │
│                                         │
│  [Retry Analysis]  [Contact Support]    │
│                                         │
│  Error Code: 500 (Show Details ▼)       │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.2

---

### FR-FE4: Results Visualization

#### FR-FE4.1: Overall Score Display
**Description:** Prominently display overall match score with clear visual representation.

**Requirements:**
- **Score Number:** Large font, highly visible (e.g., 48-72px)
- **Visual Indicator:** Gauge, progress circle, or bar chart
- **Color Coding:**
  - Red (0-49): Poor match
  - Yellow (50-74): Fair match
  - Green (75-100): Good match
- **Interpretive Label:** "Poor Match", "Fair Match", "Good Match", "Excellent Match"
- **Summary Statement:** 2-3 sentence summary of overall fit

**UI Elements:**
```
┌─────────────────────────────────────────┐
│        Analysis Results                 │
│                                         │
│           ┌─────────┐                   │
│           │   75    │  Good Match       │
│           │  ━━━◉━  │                   │
│           └─────────┘                   │
│                                         │
│  Your CV is a good match for this role. │
│  You have most required skills, but     │
│  could strengthen your leadership       │
│  experience and add some keywords.      │
└─────────────────────────────────────────┘
```

**Accessibility:**
- Score announced to screen readers with interpretation
- Color not sole indicator (use icons/text as well)
- Sufficient contrast ratios (WCAG AA)

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.3, FR4.1

---

#### FR-FE4.2: Subscores Breakdown
**Description:** Display detailed subscores for transparency and actionability.

**Requirements:**
- **Four Subscores:**
  1. Skills Match (out of 100)
  2. Experience Match (out of 100)
  3. Keyword Match (out of 100)
  4. Education Match (out of 100)
- **Visual Representation:** Horizontal bar charts or progress bars
- **Percentage Labels:** Numeric score displayed
- **Tooltip Explanations:** Hover/tap for explanation of each subscore
- **Color Consistency:** Same color scheme as overall score
- **Expandable Details:** Click to see detailed breakdown

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  Score Breakdown                        │
│                                         │
│  Skills Match         ███████░░░ 80/100 │
│  Experience Match     ██████░░░░ 70/100 │
│  Keyword Match        ███████░░░ 75/100 │
│  Education Match      ████████░ 85/100  │
│                                         │
│  (i) Tap any score for details          │
└─────────────────────────────────────────┘
```

**Tooltip Content Example (Skills Match):**
"Skills Match measures how many required and preferred skills from the job description are present in your CV. You matched 12 out of 15 required skills."

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.3, FR3.1, FR3.5

---

#### FR-FE4.3: Top Strengths & Improvements
**Description:** Highlight key takeaways from analysis.

**Requirements:**
- **Top 3 Strengths:** What CV does well for this role
- **Top 3 Improvements:** Highest-impact changes to make
- **Bullet Point Format:** Concise, scannable list
- **Icon Indicators:** ✓ for strengths, ⚠ for improvements
- **Link to Details:** "See all recommendations ↓"

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  ✓ Top Strengths                        │
│  • Strong Python and FastAPI skills     │
│  • Relevant API development experience  │
│  • AWS certification aligns well        │
│                                         │
│  ⚠ Areas to Improve                     │
│  • Add PostgreSQL to skills             │
│  • Emphasize leadership experience      │
│  • Include architecture keywords        │
│                                         │
│  [View Detailed Recommendations ↓]      │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.3, FR4.1

---

#### FR-FE4.4: Recommendations List
**Description:** Display comprehensive, prioritized, actionable recommendations.

**Requirements:**
- **Categorization:** Group by type
  - ➕ Add (missing skills, keywords, experiences)
  - ✏️ Modify (rephrase, expand, restructure)
  - ⭐ Emphasize (make more prominent)
  - ➖ Remove (de-emphasize, condense)
- **Priority Indicators:** High, Medium, Low (visual badges)
- **Sortable/Filterable:** By priority, by category
- **Expandable Cards:** Click to expand for full details
- **Each Recommendation Includes:**
  - Title (concise action)
  - Category icon and priority badge
  - Short description (1-2 sentences)
  - Rationale (why it matters) - *Note: Phase 2 may return simple recommendations as strings*
  - Example (how to implement) - *Note: May not be available in initial backend version*
  - Expected impact (e.g., "+5 points to score") - *Note: Future enhancement*
- **Minimum Display:** 5 recommendations
- **Action Tracking (Future):** Checkbox to mark as "implemented"

**⚠️ Backend Alignment Note:** 
Current backend (Phase 1) returns recommendations as a simple `string[]` array. The frontend should:
1. Display recommendations as a list initially
2. Design UI to accommodate future structured recommendation objects when backend is enhanced
3. Use placeholder data for rationale/examples in mockups
4. Plan for backend API evolution in Phase 3

**Fallback Display Strategy (Phase 2):**
If backend returns simple strings:
- Display each recommendation in a card
- Auto-infer priority based on position (first 3 = High, next 3 = Medium, rest = Low)
- Omit rationale and examples (or use generic placeholders)
- Focus on clear, scannable list presentation

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  Recommendations (8)                    │
│                                         │
│  Filter: [All] [High] [Medium] [Low]    │
│  Sort: [Priority ▼] [Category]          │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ ➕ Add PostgreSQL to Skills  [HIGH]│  │
│  │ The job requires PostgreSQL...    │  │
│  │ [Expand for details ▼]            │  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ ⭐ Emphasize Leadership     [HIGH]│  │
│  │ Your CV mentions 'Led team'...    │  │
│  │ [Expand for details ▼]            │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [Load More]                            │
└─────────────────────────────────────────┘
```

**Expanded Recommendation (Future):**
```
┌─────────────────────────────────────────┐
│ ➕ Add PostgreSQL to Skills  [HIGH]     │
│                                         │
│ Description:                            │
│ The job requires PostgreSQL experience, │
│ but it's not listed in your CV.         │
│                                         │
│ Why it matters:                         │
│ PostgreSQL is a required skill. If you  │
│ have experience with it, add it         │
│ prominently. If not, consider learning. │
│                                         │
│ How to implement:                       │
│ Add 'PostgreSQL' to your skills section │
│ or mention a project where you used it: │
│ "Built REST API with FastAPI and        │
│ PostgreSQL database for data storage."  │
│                                         │
│ Expected impact: +5 points              │
│                                         │
│ [Collapse ▲]  [Mark as Done]            │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.3, FR4.2-FR4.6

---

### FR-FE5: Analysis History

#### FR-FE5.1: History List View
**Description:** Display list of past analyses for the current session/user.

**Requirements:**
- **List Display:** Card-based or table-based layout
- **Each Entry Shows:**
  - Analysis date and time
  - Overall score (with color coding)
  - Job title (if extracted) or "Job [ID]"
  - CV filename or "CV [ID]"
  - Quick action: "View Details"
- **Sorting Options:** 
  - By date (newest first, oldest first)
  - By score (highest first, lowest first)
- **Filtering (Future):** By score range, by date range
- **Pagination:** 10 results per page
- **Empty State:** Friendly message when no history exists

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  Analysis History                       │
│                                         │
│  Sort by: [Date (Newest) ▼]             │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ Dec 31, 2025 - 2:30 PM           │  │
│  │ Score: 75  [Good Match]           │  │
│  │ CV: john_doe_cv.md                │  │
│  │ Job: Senior Software Engineer     │  │
│  │                   [View Details →]│  │
│  └───────────────────────────────────┘  │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │ Dec 30, 2025 - 4:15 PM           │  │
│  │ Score: 62  [Fair Match]           │  │
│  │ CV: john_doe_cv.md                │  │
│  │ Job: Product Manager              │  │
│  │                   [View Details →]│  │
│  └───────────────────────────────────┘  │
│                                         │
│  Showing 1-10 of 23  [Next Page →]      │
└─────────────────────────────────────────┘
```

**Empty State:**
```
┌─────────────────────────────────────────┐
│  Analysis History                       │
│                                         │
│           📊                            │
│                                         │
│  No analyses yet!                       │
│                                         │
│  Upload a CV and analyze it against a   │
│  job description to get started.        │
│                                         │
│  [Start New Analysis]                   │
└─────────────────────────────────────────┘
```

**Priority:** P1 (Should Have)  
**Related PRD:** AC2.4, FR5.1, FR5.2

---

#### FR-FE5.2: View Past Analysis
**Description:** Retrieve and display full details of a previous analysis.

**Requirements:**
- **Navigation:** Click on history entry to view full results
- **Display:** Same format as fresh analysis results
- **Read-Only:** Clearly indicate this is a past analysis (timestamp badge)
- **Actions Available:**
  - View full recommendations
  - Re-analyze with same CV and job (create new analysis)
  - Delete analysis (Phase 3 with user accounts)
- **Back Navigation:** Return to history list

**Priority:** P1 (Should Have)  
**Related PRD:** AC2.4, FR5.2

---

#### FR-FE5.3: Score Comparison (Future)
**Description:** Compare scores across multiple analyses.

**Requirements:**
- Select 2-4 analyses to compare
- Side-by-side score display
- Highlight improvements/declines
- Visual chart (line graph or bar chart)

**Priority:** P3 (Won't Have - Phase 3)  
**Related PRD:** FR5.3 (Future)

---

### FR-FE6: Tabbed Analysis Report Interface

#### FR-FE6.1: Tab Navigation Component
**Description:** Implement a tabbed interface to organize analysis results into three distinct sections.

**Requirements:**
- **Three Tabs:**
  1. CV Document
  2. Job Description
  3. Analysis Results
- **Tab UI Elements:**
  - Horizontal tab bar at top of results section
  - Each tab shows label text
  - Active tab visual indicator (underline, color change, or background highlight)
  - Inactive tabs styled subtly (lower opacity or neutral color)
- **Tab State Management:**
  - Track active tab in application state (`activeTab: 'cv' | 'job' | 'results'`)
  - Default active tab: "Analysis Results"
  - Persist active tab using `sessionStorage` key `cv-checker:active-tab`
  - Restore tab state on page reload within same session
- **Keyboard Navigation:**
  - Arrow keys (←/→) navigate between tabs
  - Tab key moves focus to tab, then into tab content
  - Enter/Space activates focused tab
- **Accessibility:**
  - ARIA role `tablist` on container
  - ARIA role `tab` on each tab button
  - ARIA role `tabpanel` on content area
  - `aria-selected="true"` on active tab
  - `aria-controls` linking tab to its panel
  - `aria-labelledby` on panel referencing tab
- **Responsive Behavior:**
  - Desktop/Tablet: Full-width horizontal tabs
  - Mobile: May condense to scrollable horizontal tabs or dropdown selector

**UI Elements:**
```
┌─────────────────────────────────────────┐
│  [CV Document] [Job Description] [Analysis Results*] │
│─────────────────────────────────────────│
│                                         │
│  (Active tab content displayed here)    │
│                                         │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** Feature 4B

---

#### FR-FE6.2: CV Document Tab
**Description:** Display the CV content from the analysis response in a formatted, readable view.

**Requirements:**
- **Data Source:**
  - CV content comes from `result.cv_markdown` in the analysis response
  - This ensures consistency for both current and historical analyses
  - Frontend doesn't need to maintain separate CV state for display
  - Same CV content is guaranteed for the analysis being viewed
- **Markdown Rendering:**
  - Use `react-markdown` library for Markdown-to-HTML conversion
  - Apply professional styling for readability:
    - Headings (h1-h6) with hierarchical sizing
    - Lists (ul, ol) with proper indentation
    - Code blocks with syntax highlighting (if present)
    - Links styled and functional
    - Blockquotes, horizontal rules, tables
- **Styling:**
  - Consistent with AG-UI theme
  - Maximum content width (e.g., 800px) for optimal readability
  - Adequate line height (1.6-1.8) and spacing
  - Font size appropriate for body text (14-16px)
- **XSS Protection:**
  - Use `remark-gfm` plugin for GitHub Flavored Markdown support
  - Use `rehype-sanitize` plugin to strip dangerous HTML
  - Never use `dangerouslySetInnerHTML` without sanitization
  - Only allow safe HTML tags and attributes
- **Empty State:**
  - If no CV available in response, display message:
    ```
    No CV available
    
    This analysis may be corrupted or incomplete.
    ```
- **Scrolling:**
  - Tab content area has independent scroll
  - Scroll position resets when switching tabs
  - Smooth scrolling behavior

**Example Rendered CV:**
```
┌─────────────────────────────────────────┐
│  CV Document                            │
│─────────────────────────────────────────│
│  # John Doe                             │
│  Software Engineer                      │
│                                         │
│  ## Experience                          │
│  **Senior Developer** - Acme Corp       │
│  2020-2025                              │
│                                         │
│  - Led team of 5 engineers             │
│  - Built scalable APIs with FastAPI    │
│                                         │
│  ## Skills                              │
│  Python, JavaScript, React, Azure       │
│  (... rest of CV content ...)           │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** Feature 4B.1

---

#### FR-FE6.3: Job Description Tab
**Description:** Display the job description from the analysis response with formatting and source information.

**Requirements:**
- **Data Source:**
  - Job description comes from `result.job_description` in the analysis response
  - Source information from `result.source_type` and `result.source_url`
  - This ensures the job description matches what was analyzed
  - Works for both current and historical analyses
- **Content Display:**
  - Render job description as formatted text
  - If job description contains Markdown, use same renderer as CV tab
  - Otherwise, display as plain text with line breaks preserved
  - Apply professional styling (same as CV tab)
- **Source Indicator:**
  - Display source information above job description based on `result.source_type`:
    - "Manually entered" - if `source_type === 'manual'`
    - "From LinkedIn: [URL]" - if `source_type === 'linkedin_url'` and `source_url` is present
  - Source displayed in small, muted text
  - LinkedIn URL (if present) is a clickable link
- **XSS Protection:**
  - Same sanitization as CV tab using `rehype-sanitize`
  - Render as plain text if not Markdown
  - Never execute scripts or render unsafe HTML
- **Empty State:**
  - If no job description in response, display:
    ```
    No job description available
    
    This analysis may be corrupted or incomplete.
    ```
- **Long Content Handling:**
  - Scrollable content area
  - No truncation (show full description)
  - Maximum width for readability (800px)
- **Layout:**
  - Source indicator at top
  - Job description content below
  - Adequate spacing between sections

**Example Job Description Tab:**
```
┌─────────────────────────────────────────┐
│  Job Description                        │
│─────────────────────────────────────────│
│  Source: Manually entered               │
│                                         │
│  Senior Software Engineer               │
│                                         │
│  We are seeking an experienced Python   │
│  developer to join our team...          │
│                                         │
│  Requirements:                          │
│  • 5+ years Python experience           │
│  • FastAPI or similar framework         │
│  • Cloud experience (Azure/AWS)         │
│  (... rest of job description ...)      │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** Feature 4B.2

---

#### FR-FE6.4: Analysis Results Tab
**Description:** Display comprehensive analysis results (existing ResultsDisplay component).

**Requirements:**
- **Content:**
  - Same content as current ResultsDisplay component
  - Overall score with gauge/progress indicator
  - Subscores breakdown (Skills, Experience, Keywords, Education)
  - Top strengths (3-5 items)
  - Top gaps/areas to improve (3-5 items)
  - Full recommendations list (categorized, prioritized)
- **Functionality:**
  - All existing interactions maintained:
    - Expandable recommendation cards
    - Filter/sort recommendations
    - Tooltips on subscores
    - Click to expand details
- **Layout:**
  - No changes to existing results layout
  - Component rendered within tab panel
  - Independent scroll context
- **Default Tab:**
  - Analysis Results tab is active by default when results load
  - After analysis completes, user sees results first
  - User can navigate to CV/Job tabs to review context

**UI Structure:**
```
┌─────────────────────────────────────────┐
│  Analysis Results                       │
│─────────────────────────────────────────│
│           ┌─────────┐                   │
│           │   75    │  Good Match       │
│           │  ━━━◉━  │                   │
│           └─────────┘                   │
│                                         │
│  Score Breakdown                        │
│  Skills Match         ███████░░░ 80/100 │
│  Experience Match     ██████░░░░ 70/100 │
│  (... rest of results ...)              │
└─────────────────────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** Feature 4B.3

---

#### FR-FE6.5: Responsive Tab Design
**Description:** Ensure tabs work seamlessly across all device sizes.

**Requirements:**
- **Desktop (1024px+):**
  - Horizontal tab bar with full label text
  - Tabs evenly spaced or left-aligned
  - Hover states on inactive tabs (subtle highlight)
  - Minimum tab width: 120px
  - Click to activate tab
- **Tablet (768-1023px):**
  - Horizontal tab bar (may condense slightly)
  - Full labels or slightly abbreviated (e.g., "CV", "Job", "Results")
  - Touch-friendly tab targets (minimum 40x40px)
  - No hover states (touch-only)
- **Mobile (320-767px):**
  - **Option 1:** Horizontal scrollable tabs
    - Swipe left/right to see all tabs
    - Active tab scrolls into view
    - Fade indicators at edges if tabs overflow
  - **Option 2:** Dropdown selector
    - Button shows current tab name with dropdown icon
    - Tap to show tab list menu
    - Select tab from menu
  - Minimum touch target: 44x44px per tab
  - Consider vertical screen space (tabs don't take too much height)
- **Adaptive Behavior:**
  - Tab labels may shorten on smaller screens:
    - "CV Document" → "CV"
    - "Job Description" → "Job"
    - "Analysis Results" → "Results"
  - Icons optional (add visual reinforcement)
- **Touch Gestures (Future Enhancement):**
  - Swipe left/right on content area to switch tabs (Phase 3)

**Responsive Examples:**

Desktop:
```
┌────────────────────────────────────────────────┐
│ [CV Document]  [Job Description]  [Analysis Results*] │
└────────────────────────────────────────────────┘
```

Mobile (Scrollable):
```
┌────────────────────────┐
│ [CV] [Job] [Results*] ─→│
└────────────────────────┘
```

Mobile (Dropdown):
```
┌────────────────────────┐
│ Results ▼              │
└────────────────────────┘
```

**Priority:** P0 (Must Have)  
**Related PRD:** Feature 4B, AC2.1

---

#### FR-FE6.6: Performance Optimization
**Description:** Ensure tab switching is smooth and responsive.

**Requirements:**
- **Lazy Rendering:**
  - Only render active tab content initially
  - Render other tabs on first activation
  - Cache rendered content to avoid re-rendering on subsequent visits
  - Use React.lazy() or conditional rendering
- **Tab Switching Performance:**
  - Tab switch response time: <100ms
  - Smooth transition (no visible lag)
  - No flash of unstyled content
  - Content appears instantly when tab clicked
- **Markdown Rendering Optimization:**
  - Parse Markdown once and cache result
  - Memoize rendered components
  - Use React.memo() for static content
  - Avoid re-parsing on tab switch
- **Memory Management:**
  - Limit number of cached tabs (max 3 - all current tabs)
  - Clean up when leaving results page
  - Monitor memory usage for large CVs/job descriptions
- **Monitoring:**
  - Track tab switching performance in Application Insights
  - Log slow switches (>200ms) for investigation
  - Custom event: `tab_switched` with timing data

**Performance Targets:**
- Tab switch: <100ms (p95)
- Markdown parsing: <50ms for typical CV (2-3 pages)
- Memory usage: <10MB for tab content

**Priority:** P1 (Should Have)  
**Related PRD:** Performance Requirements

---

## UI/UX Requirements

### UX-1: Responsive Design

#### UX-1.1: Mobile Layout (320px - 767px)
**Requirements:**
- **Single Column Layout:** All components stack vertically
- **Touch-Friendly Targets:** Minimum 44x44px touch targets
- **Simplified Navigation:** Hamburger menu for secondary actions
- **Condensed Score Display:** Vertical gauge or simplified bar
- **Recommendations:** Accordions for space efficiency
- **File Upload:** Full-width drop zone

**Mobile-Specific Considerations:**
- Large, tappable buttons
- Avoid hover-dependent interactions
- Optimize for slow connections (lazy loading, skeleton screens)
- Minimize text entry (auto-capitalization, appropriate keyboard types)

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1, AC2.5

---

#### UX-1.2: Tablet Layout (768px - 1023px)
**Requirements:**
- **Two-Column Layout:** CV upload + job input side-by-side
- **Optimized Touch Targets:** Slightly smaller than mobile (40x40px minimum)
- **Expanded Visualization:** Larger score gauge and charts
- **Side Panel Option:** History accessible via slide-out panel

**Priority:** P0 (Must Have)

---

#### UX-1.3: Desktop Layout (1024px+)
**Requirements:**
- **Multi-Column Layout:** Efficient use of horizontal space
- **Enhanced Visualizations:** Full-size charts and graphs
- **Hover Interactions:** Tooltips, hover states for enrichment
- **Keyboard Navigation:** Full keyboard accessibility
- **Side Navigation:** Persistent history sidebar (optional)

**Priority:** P0 (Must Have)

---

### UX-2: Accessibility (WCAG 2.1 AA)

#### UX-2.1: Keyboard Navigation
**Requirements:**
- **Tab Order:** Logical, intuitive tab sequence
- **Focus Indicators:** Visible focus states (2px outline minimum)
- **Keyboard Shortcuts:** Common shortcuts (Enter to submit, Esc to cancel)
- **Skip Links:** "Skip to main content" for screen readers
- **No Keyboard Traps:** All interactive elements escapable

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1

---

#### UX-2.2: Screen Reader Support
**Requirements:**
- **Semantic HTML:** Proper use of headings, landmarks, lists
- **ARIA Labels:** Descriptive labels for all interactive elements
- **Alt Text:** Meaningful alt text for images and icons
- **Live Regions:** Announce dynamic content changes (loading states, errors)
- **Form Labels:** Explicit labels for all inputs

**Priority:** P0 (Must Have)

---

#### UX-2.3: Color & Contrast
**Requirements:**
- **Contrast Ratios:**
  - 4.5:1 for normal text
  - 3:1 for large text (18px+ or 14px+ bold)
  - 3:1 for UI components and graphics
- **Color Independence:** Information not conveyed by color alone
- **Focus Indicators:** High contrast for keyboard focus

**Testing Tools:** WebAIM Contrast Checker, axe DevTools

**Priority:** P0 (Must Have)

---

#### UX-2.4: Text Scaling
**Requirements:**
- **Zoom Support:** Content readable at 200% zoom without horizontal scroll
- **Relative Units:** Use rem/em instead of px for fonts
- **Responsive Text:** Font sizes adjust based on viewport
- **No Text Truncation:** Text reflows, doesn't get cut off

**Priority:** P0 (Must Have)

---

### UX-3: Loading States & Feedback

#### UX-3.1: Optimistic UI Updates
**Requirements:**
- **Immediate Feedback:** Button state changes instantly on click
- **Skeleton Screens:** Show content structure while loading
- **Progressive Disclosure:** Display results as they become available

**Priority:** P1 (Should Have)

---

#### UX-3.2: Error Recovery
**Requirements:**
- **Preserve User Input:** Don't lose data on error
- **Clear Error Messages:** Specific, actionable guidance
- **Retry Mechanisms:** Easy path to retry failed actions
- **Graceful Degradation:** Partial results if possible

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.2

---

### UX-4: Success & Confirmation

#### UX-4.1: Success Messages
**Requirements:**
- **Upload Success:** "✓ CV uploaded successfully: [filename]"
- **Analysis Complete:** "✓ Analysis complete! Scroll down to view results."
- **Auto-Dismiss:** Success messages fade after 5 seconds
- **Persistent Option:** Critical confirmations stay visible
- **Accessible Announcements:** Screen reader notifications

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.2

---

#### UX-4.2: Progress Tracking
**Requirements:**
- **Multi-Step Indicator:** Show current step (1. Upload CV → 2. Add Job → 3. Analyze → 4. Results)
- **Completion Percentage:** For multi-stage processes
- **Visual Checkmarks:** Completed steps marked

**Priority:** P1 (Should Have)

---

### UX-5: Performance

#### UX-5.1: Load Time Optimization
**Requirements:**
- **First Contentful Paint:** <1.5 seconds
- **Time to Interactive:** <3 seconds
- **Code Splitting:** Lazy load non-critical components
- **Asset Optimization:** Compressed images, minified CSS/JS
- **CDN Delivery:** Serve static assets from CDN

**Priority:** P1 (Should Have)

---

#### UX-5.2: Runtime Performance
**Requirements:**
- **Smooth Scrolling:** 60fps scroll performance
- **Responsive Interactions:** <100ms response to user input
- **Efficient Re-renders:** Optimize component updates
- **Memory Management:** No memory leaks

**Priority:** P1 (Should Have)

---

## Technical Requirements

### TECH-1: AG-UI Framework Integration

#### TECH-1.1: Framework Setup
**Requirements:**
- Install and configure AG-UI framework
- Set up recommended project structure
- Configure build tools (Webpack/Vite as per AG-UI docs)
- Integrate AG-UI theming system
- Set up development environment with hot reload

**Priority:** P0 (Must Have)

**⚠️ CRITICAL NOTE:** AG-UI framework availability requires verification. If AG-UI is not yet publicly available or lacks sufficient documentation:
- **Fallback Option 1:** Use Fluent UI 2 (React) as the Microsoft design system foundation
- **Fallback Option 2:** Use React with Azure Static Web Apps + standard UI libraries (MUI, Radix UI)
- **Action Required:** Verify AG-UI documentation and availability before Phase 2 kickoff

---

#### TECH-1.2: Component Library Usage
**Requirements:**
- Use AG-UI native components where available:
  - Button, Input, Textarea
  - Card, Modal, Tooltip
  - Progress indicators, Spinners
  - Alert, Toast notifications
  - Layout components (Grid, Flex)
- Custom components only when AG-UI doesn't provide
- Follow AG-UI component API conventions
- Implement AG-UI accessibility patterns

**Priority:** P0 (Must Have)

---

### TECH-2: API Integration

#### TECH-2.1: Backend API Contract
**Requirements:**
- **Backend API Base URL:** Configurable via environment variable (e.g., `VITE_API_BASE_URL`)
- **Primary Endpoint:** `POST /api/v1/analyze`
  - **Request Body:**
    ```typescript
    {
      cv_markdown: string;      // Min 100 chars, max 50,000 chars
      job_description: string;  // Min 50 chars, max 10,000 chars
    }
    ```
  - **Response Body:**
    ```typescript
    {
      analysis_id: string;
      overall_score: number;    // 0-100
      skill_matches: SkillMatch[];
      experience_match: object;
      education_match: object;
      strengths: string[];
      gaps: string[];
      recommendations: string[];
    }
    ```
- **Health Check Endpoint:** `GET /api/v1/health`
- **OpenAPI Spec Location:** `http://localhost:8000/api/v1/openapi.json` (dev) or production URL

**Validation:**
- Request payloads must match backend validation rules (see [backend/app/models/requests.py](../../backend/app/models/requests.py))
- Frontend must enforce same min/max length constraints as backend
- Handle backend error responses (400, 422, 500) with user-friendly messages

**Priority:** P0 (Must Have)  
**Related Documents:** ADR-005, backend/README.md

---

#### TECH-2.2: OpenAPI Client Generation
**Requirements:**
- **Client Generator:** Use `@openapitools/openapi-generator-cli` or `openapi-typescript-codegen`
- **Generation Command:** 
  ```bash
  npx openapi-typescript-codegen --input http://localhost:8000/api/v1/openapi.json --output ./src/api/generated --client axios
  ```
- **Generated Artifacts:**
  - TypeScript types for request/response models
  - API service class with type-safe methods
  - Runtime validation (optional)
- **Regeneration Trigger:** When backend OpenAPI spec changes (detected in CI/CD)
- **API Base URL Configuration:** Environment variable `VITE_API_BASE_URL`
- **Request/Response Interceptors:**
  - Add `Content-Type: application/json` header
  - Add request ID for tracing (optional)
  - Log errors to Application Insights
- **Timeout Configuration:**
  - Analysis endpoint: 60s (analysis can take 20-30s)
  - Health check: 5s
  - Default: 10s

**Priority:** P0 (Must Have)  
**Related PRD:** AC1.6

---

#### TECH-2.3: API Error Handling Strategy
**Requirements:**
- **HTTP 400 (Bad Request):** 
  - Display validation error message to user
  - Example: "Your CV is too short. Please provide at least 100 characters."
- **HTTP 422 (Validation Error):**
  - Parse Pydantic validation errors
  - Show field-specific error messages
  - Example: "CV markdown: Content cannot be empty"
- **HTTP 500 (Server Error):**
  - Generic user message: "Analysis failed. Please try again."
  - Log full error details to Application Insights
  - Show "Retry" button
- **Network Errors:**
  - Message: "Unable to connect. Please check your internet connection."
  - Retry mechanism with exponential backoff (1s, 2s, 4s)
- **Timeout Errors:**
  - Message: "Analysis is taking longer than expected. Please try again."
  - Cancel in-progress request
- **Error Response Structure (from backend):**
  ```typescript
  {
    error: string;        // Error type (e.g., "ValidationError")
    message: string;      // Human-readable message
    details?: object;     // Additional context
  }
  ```

**Priority:** P0 (Must Have)

---

#### TECH-2.4: State Management
**Requirements:**
- **State Management Library:** 
  - AG-UI recommended approach (if available)
  - **Fallback:** Zustand (lightweight, TypeScript-first) or React Context API
- **State Structure:**
  ```typescript
  {
    // Input state - for submission only
    currentCv: {
      filename: string | null;
      content: string | null;
      uploadedAt: string | null;
    },
    currentJob: {
      description: string;
      sourceType: 'manual' | 'linkedin_url';
      sourceUrl?: string;
      lastModified: string | null;
    },
    // Analysis state
    currentAnalysis: {
      isLoading: boolean;
      error: string | null;
      result: AnalyzeResponse | null;  // Includes cv_markdown and job_description
    },
    analysisHistory: AnalyzeResponse[];  // Last 10 analyses
  }
  ```
- **Data Flow:**
  - **For Submission:** Frontend collects CV and job description from user input
  - **For Display:** After analysis, CV and job data come from `result.cv_markdown` and `result.job_description`
  - **History Display:** All CV/job content displayed from stored `AnalyzeResponse` objects
  - This ensures displayed content always matches what was analyzed
- **Persistence:** 
  - LocalStorage for current CV/job (pre-submission) and history
  - Session key: `cv-checker-session-${userId || 'anonymous'}`
  - Maximum storage: 5MB (monitor quota)
- **State Actions:**
  - `uploadCV(file)`, `clearCV()`
  - `updateJobDescription(text, sourceType, sourceUrl?)`, `clearJob()`
  - `startAnalysis()`, `completeAnalysis(result)`, `failAnalysis(error)`
  - `loadHistory()`, `clearHistory()`
- **Concurrency Handling:** 
  - Disable "Analyze" button during in-progress analysis
  - Cancel previous request if new analysis started

**Priority:** P0 (Must Have)

---

#### TECH-2.5: Authentication (Phase 3)
**Requirements:**
- Placeholder for future auth integration
- Design with auth in mind (user context)
- No authentication required in Phase 2

**Priority:** P3 (Won't Have - Phase 3)

---

### TECH-3: Data Handling & Security

#### TECH-3.1: Local Storage Management
**Requirements:**
- **Storage Strategy:**
  - Use `localStorage` for persistence across sessions
  - Namespace keys: `cv-checker:cv`, `cv-checker:job`, `cv-checker:history`
  - Serialize/deserialize with JSON.stringify/parse
- **Data Retention:**
  - CV and job: Until user clears or replaces
  - Analysis history: Last 10 results, max 7 days
  - Auto-cleanup on app initialization (remove expired data)
- **Storage Quota Handling:**
  - Monitor available quota (5MB typical limit)
  - Show warning if >80% used: "Your analysis history is almost full. Consider clearing old results."
  - Auto-delete oldest history entries if quota exceeded
- **Privacy Considerations:**
  - Clear all data on "Clear Session" action
  - No PII stored (CV content only, no names/emails)
  - Inform users data is stored locally (privacy notice)

**Priority:** P1 (Should Have)

---

#### TECH-3.2: File Upload Security & Validation
**Requirements:**
- **Client-Side Validation:**
  - **File Extension:** Must be `.md` (case-insensitive)
  - **MIME Type Check:** Verify `text/markdown` or `text/plain`
  - **File Size:** Maximum 2MB (2,097,152 bytes)
  - **Content Validation:** 
    - Check for minimum 100 characters after whitespace trimming
    - Warn if no Markdown headers detected (# symbols)
- **File Reading:**
  - Use FileReader API with async/await wrapper
  - Handle encoding issues (assume UTF-8)
  - Show loading spinner during file read
- **XSS Prevention:**
  - **DO NOT** render Markdown as HTML in the frontend
  - Display CV content as plain text in preview (optional feature)
  - Backend handles all Markdown parsing
- **Content Sanitization:**
  - Strip null bytes (`\0`) from file content
  - Normalize line endings (CRLF → LF)
  - Remove excessive whitespace (>2 consecutive newlines)
- **Error Messages:**
  - "Invalid file format. Please upload a Markdown (.md) file."
  - "File too large. Maximum size is 2MB. Your file is {size}MB."
  - "Failed to read file. Please try a different file."

**Priority:** P0 (Must Have)

---

#### TECH-3.3: Input Sanitization (Job Description)
**Requirements:**
- **Client-Side Validation:**
  - Minimum length: 100 characters (after trim)
  - Maximum length: 50,000 characters
  - Character counter updates in real-time
- **Content Sanitization:**
  - Trim leading/trailing whitespace
  - Normalize line endings
  - Remove control characters except newlines and tabs
  - No HTML/script tag rendering (display as plain text)
- **XSS Prevention:**
  - Never use `dangerouslySetInnerHTML` for user input
  - Use text content rendering only
  - Escape special characters if displaying in HTML context

**Priority:** P0 (Must Have)

---

### TECH-4: Error Handling & Logging

#### TECH-4.1: Error Boundaries
**Requirements:**
- **React Error Boundary Implementation:**
  - Top-level boundary wrapping entire app
  - Component-level boundaries for major sections (Upload, Results, History)
- **Fallback UI:**
  - User-friendly error message: "Something went wrong. Please refresh the page."
  - "Refresh Page" and "Report Issue" buttons
  - Don't expose stack traces to users (log only)
- **Error Logging:**
  - Development: Console logging with full stack trace
  - Production: Send to Azure Application Insights
    - Error message, stack trace, component tree
    - User context (browser, viewport, timestamp)
    - Last user action (breadcrumb trail)
- **Recovery Strategy:**
  - Persist unsaved data (CV, job description) to localStorage before crash
  - Restore state on page refresh

**Priority:** P1 (Should Have)

---

#### TECH-4.2: Application Insights Integration
**Requirements:**
- **Azure Application Insights Setup:**
  - Install `@microsoft/applicationinsights-web`
  - Initialize with instrumentation key (environment variable)
  - Enable auto-collection: page views, AJAX calls, exceptions
- **Custom Event Tracking:**
  - User actions:
    - `cv_uploaded` (file size, processing time)
    - `job_description_entered` (character count)
    - `analysis_started`
    - `analysis_completed` (score, duration)
    - `analysis_failed` (error type)
    - `recommendation_viewed` (priority, category)
  - Performance:
    - Page load time (First Contentful Paint, Time to Interactive)
    - API latency (request duration, status code)
    - File upload time
- **Privacy Compliance:**
  - **DO NOT** log PII: names, email addresses, phone numbers
  - **DO NOT** log CV content or job descriptions
  - Log only metadata: file size, character count, analysis duration
  - Hash analysis IDs for correlation (don't expose raw IDs)
- **Sampling:**
  - Development: 100% sampling
  - Production: 10% sampling for telemetry, 100% for errors

**Priority:** P1 (Should Have)

---

#### TECH-4.3: Logging & Analytics
**Requirements:**
- **Logging Levels:**
  - Development: Debug, Info, Warn, Error
  - Production: Info, Warn, Error only
- **Structured Logging:**
  - Use JSON format for log entries
  - Include: timestamp, level, message, context (user action, component)
- **Analytics Metrics:**
  - User engagement: completion rate, time to first analysis, repeat usage
  - Performance: API latency p50/p95/p99, page load time
  - Errors: error rate by type, affected user count
- **Privacy-Compliant Analytics:**
  - No PII in logs or analytics
  - Anonymous session IDs only
  - User consent for analytics (cookie banner - Phase 3)

**Priority:** P1 (Should Have)

---

### TECH-5: Build & Deployment

#### TECH-5.1: Build Configuration
**Requirements:**
- **Build Tool:** Vite (recommended for modern React apps)
  - Fast HMR (Hot Module Replacement)
  - ESM-based, optimized for production
  - Built-in TypeScript support
- **Production Optimizations:**
  - Code minification (Terser)
  - Tree-shaking (remove unused code)
  - CSS minification
  - Asset optimization (image compression, lazy loading)
  - Code splitting by route
- **Environment Variables:**
  - `.env.local` (local development, git-ignored)
  - `.env.production` (production settings)
  - Required variables:
    - `VITE_API_BASE_URL`: Backend API URL
    - `VITE_APP_INSIGHTS_KEY`: Application Insights instrumentation key
    - `VITE_ENV`: `development` | `staging` | `production`
- **Source Maps:**
  - Development: Full inline source maps
  - Production: Separate `.map` files, uploaded to Azure for debugging
- **TypeScript Configuration:**
  - Strict mode enabled
  - No implicit any
  - ESLint + Prettier integration

**Build Output Structure:**
```
dist/
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── [images/fonts]
├── index.html
└── favicon.ico
```

**Priority:** P1 (Should Have)

---

#### TECH-5.2: Azure Static Web Apps Deployment
**Requirements:**
- **Deployment Target:** Azure Static Web Apps
  - Free tier for MVP (10GB bandwidth/month, custom domain support)
  - Automatic HTTPS
  - Global CDN distribution
- **GitHub Actions CI/CD:**
  - Trigger: Push to `main` branch or manual workflow dispatch
  - Steps:
    1. Checkout code
    2. Install dependencies (`npm ci`)
    3. Run tests (`npm test`)
    4. Run linter (`npm run lint`)
    5. Build production bundle (`npm run build`)
    6. Deploy to Azure Static Web Apps (Azure/static-web-apps-deploy action)
  - Environments: `staging` (on PR), `production` (on merge to main)
- **CORS Configuration:**
  - Backend must allow frontend origin
  - Development: `http://localhost:5173` (Vite default)
  - Production: `https://<app-name>.azurestaticapps.net`
- **Custom Domain (Optional):**
  - Configure in Azure portal
  - SSL certificate auto-provisioned
- **Monitoring:**
  - Azure Static Web Apps analytics
  - Application Insights for client-side telemetry
- **Fallback Route:**
  - Configure `staticwebapp.config.json`:
    ```json
    {
      "navigationFallback": {
        "rewrite": "/index.html",
        "exclude": ["/api/*", "/assets/*"]
      }
    }
    ```

**Deployment Workflow Example:**
```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches: [main]

jobs:
  build_and_deploy_job:
    runs-on: ubuntu-latest
    name: Build and Deploy
    steps:
      - uses: actions/checkout@v3
      - name: Build And Deploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/frontend"
          api_location: ""
          output_location: "dist"
```

**Priority:** P1 (Should Have)  
**Related PRD:** Technology Stack

---

### TECH-6: Testing Strategy

#### TECH-6.1: Unit Testing
**Requirements:**
- **Test Framework:** Vitest (Vite-native, fast)
- **Test Coverage Target:** >80% for critical paths
- **Test Scope:**
  - **Utility functions:** File validation, sanitization, formatting
  - **State management:** Actions, reducers, selectors
  - **API client:** Mock HTTP calls with MSW (Mock Service Worker)
  - **Components:** Individual component logic (not full rendering)
- **Example Test Cases:**
  - `validateFile()` - rejects non-Markdown files
  - `sanitizeJobDescription()` - removes control characters
  - `analyzeCV()` API call - handles success/error responses
  - `formatScore()` - returns correct color for score range

**Priority:** P0 (Must Have)

---

#### TECH-6.2: Integration Testing
**Requirements:**
- **Test Framework:** Vitest + Testing Library
- **Test Scope:**
  - **Full user workflows:** 
    - Upload CV → Enter job → Analyze → View results
    - View history → Select past analysis → View details
  - **Error scenarios:**
    - Invalid file upload → See error message
    - API timeout → See retry button
- **Mock Strategy:**
  - Mock API calls with MSW (intercept network requests)
  - Mock file uploads with File/Blob objects
  - Mock localStorage

**Priority:** P1 (Should Have)

---

#### TECH-6.3: End-to-End Testing
**Requirements:**
- **Test Framework:** Playwright or Cypress
- **Test Environment:** Run against staging environment with real backend
- **Test Scope:**
  - Happy path: Complete analysis workflow end-to-end
  - Error path: Network failure, invalid input
  - Responsive design: Test on mobile, tablet, desktop viewports
  - Accessibility: Keyboard navigation, screen reader compatibility
- **CI/CD Integration:**
  - Run E2E tests on every PR (against staging)
  - Block merge if tests fail
- **Example E2E Test:**
  ```typescript
  test('user can complete CV analysis', async ({ page }) => {
    await page.goto('/');
    await page.setInputFiles('input[type="file"]', 'test-cv.md');
    await page.fill('textarea', 'Senior Python Developer needed...');
    await page.click('button:text("Analyze Match")');
    await expect(page.locator('.overall-score')).toBeVisible();
    await expect(page.locator('.overall-score')).toContainText(/\d+/);
  });
  ```

**Priority:** P1 (Should Have)

---

#### TECH-6.4: Accessibility Testing
**Requirements:**
- **Automated Testing:**
  - Integrate `axe-core` via `@axe-core/playwright` or `jest-axe`
  - Run on every component and page
  - Enforce WCAG 2.1 AA compliance (no violations)
- **Manual Testing:**
  - Keyboard navigation: Tab through all interactive elements
  - Screen reader: Test with NVDA (Windows) and VoiceOver (macOS/iOS)
  - Color contrast: Use WebAIM Contrast Checker
  - Text scaling: Test at 200% zoom
- **CI/CD Integration:**
  - Automated a11y tests run on every PR
  - Fail build if WCAG violations detected

**Priority:** P0 (Must Have)

---

### TECH-7: Performance Optimization

#### TECH-7.1: Loading Performance
**Requirements:**
- **Core Web Vitals Targets:**
  - **Largest Contentful Paint (LCP):** <2.5s
  - **First Input Delay (FID):** <100ms
  - **Cumulative Layout Shift (CLS):** <0.1
- **Optimization Strategies:**
  - Code splitting: Lazy load routes and heavy components
  - Asset optimization: Compress images, use WebP format
  - Critical CSS: Inline above-the-fold styles
  - Preload fonts and critical resources
  - Enable HTTP/2 server push (Azure CDN)
- **Measurement:**
  - Lighthouse CI in GitHub Actions (enforce scores >90)
  - Real User Monitoring (RUM) via Application Insights

**Priority:** P1 (Should Have)

---

#### TECH-7.2: Runtime Performance
**Requirements:**
- **Interaction Responsiveness:**
  - Button clicks: <100ms visual feedback
  - Form inputs: <16ms (60fps) re-renders
  - File upload: Show progress within 50ms
- **Optimization Strategies:**
  - React optimization: `memo()`, `useMemo()`, `useCallback()`
  - Virtualization: For long lists (history, recommendations)
  - Debouncing: Character counter, form validation
  - Web Workers: For heavy computations (Markdown preview)
- **Monitoring:**
  - Track Long Tasks (>50ms) via Performance Observer
  - Log slow interactions to Application Insights

**Priority:** P1 (Should Have)

---

### TECH-8: Security Best Practices

#### TECH-8.1: Content Security Policy (CSP)
**Requirements:**
- **CSP Headers (configured in Azure Static Web Apps):**
  ```
  Content-Security-Policy: 
    default-src 'self'; 
    script-src 'self' 'unsafe-inline' https://js.monitor.azure.com; 
    style-src 'self' 'unsafe-inline'; 
    img-src 'self' data: https:; 
    connect-src 'self' https://<backend-api>.azurewebsites.net https://dc.services.visualstudio.com;
    font-src 'self' data:;
    object-src 'none';
    base-uri 'self';
    form-action 'self';
  ```
- **Rationale:**
  - Prevent XSS attacks
  - Restrict resource loading to trusted origins
  - Allow Application Insights scripts

**Priority:** P1 (Should Have)

---

#### TECH-8.2: Dependency Security
**Requirements:**
- **Dependency Scanning:**
  - Run `npm audit` on every build
  - Fail CI/CD if critical vulnerabilities detected
  - Use Dependabot for automated security updates
- **Dependency Management:**
  - Lock dependency versions (`package-lock.json`)
  - Review dependencies before adding (prefer well-maintained packages)
  - Minimize dependency count (reduce attack surface)

**Priority:** P1 (Should Have)

---

#### TECH-8.3: Secrets Management
**Requirements:**
- **Environment Variables:**
  - **Never** commit secrets to Git (`.env.local` in `.gitignore`)
  - Use Azure Key Vault for production secrets
  - GitHub Secrets for CI/CD variables
- **API Keys:**
  - Application Insights key: Store in environment variable
  - Backend API URL: Configurable per environment

**Priority:** P0 (Must Have)

---

### TECH-9: CI/CD Pipeline

#### TECH-9.1: GitHub Actions Workflow
**Requirements:**
- **Workflow Triggers:**
  - Push to `main` branch → Deploy to production
  - Pull request opened/updated → Deploy to preview environment, run tests
  - Manual workflow dispatch → Deploy to staging
- **Workflow Steps (Build & Test):**
  ```yaml
  name: Frontend CI/CD
  
  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]
  
  jobs:
    build-test-deploy:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout code
          uses: actions/checkout@v3
        
        - name: Setup Node.js
          uses: actions/setup-node@v3
          with:
            node-version: '18'
            cache: 'npm'
        
        - name: Install dependencies
          run: npm ci
        
        - name: Lint code
          run: npm run lint
        
        - name: Type check
          run: npm run type-check
        
        - name: Run unit tests
          run: npm test -- --coverage
        
        - name: Run accessibility tests
          run: npm run test:a11y
        
        - name: Build application
          run: npm run build
          env:
            VITE_API_BASE_URL: ${{ secrets.API_BASE_URL }}
            VITE_APP_INSIGHTS_KEY: ${{ secrets.APP_INSIGHTS_KEY }}
        
        - name: Run Lighthouse CI
          run: npm run lighthouse
        
        - name: Deploy to Azure Static Web Apps
          uses: Azure/static-web-apps-deploy@v1
          with:
            azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
            repo_token: ${{ secrets.GITHUB_TOKEN }}
            action: "upload"
            app_location: "/frontend"
            output_location: "dist"
  ```

**Priority:** P1 (Should Have)

---

#### TECH-9.2: Quality Gates
**Requirements:**
- **Automated Checks (must pass before merge):**
  - ESLint: No errors allowed (warnings acceptable with justification)
  - TypeScript: No type errors
  - Unit tests: 100% passing, >80% coverage
  - Accessibility tests: No WCAG AA violations
  - Lighthouse CI: Performance >90, Accessibility >95, Best Practices >90
- **Code Review:**
  - At least 1 approval required
  - No unresolved comments
- **Preview Deployment:**
  - PR creates preview URL for manual testing
  - Comment on PR with preview URL

**Priority:** P1 (Should Have)

---

#### TECH-9.3: Deployment Environments
**Requirements:**
- **Development:** Local (`http://localhost:5173`)
  - Backend: `http://localhost:8000`
  - Hot reload enabled
  - Debug mode, verbose logging
- **Staging:** Preview deployments (`https://cv-checker-<pr-number>.azurestaticapps.net`)
  - Backend: Staging API URL
  - Application Insights enabled
  - Same as production but isolated
- **Production:** (`https://cv-checker.azurestaticapps.net`)
  - Backend: Production API URL
  - Application Insights enabled
  - Error logging only (no debug logs)
  - CDN caching enabled

**Environment-Specific Configurations:**
```typescript
// config.ts
export const config = {
  development: {
    apiBaseUrl: 'http://localhost:8000',
    appInsightsKey: '',
    logLevel: 'debug',
  },
  staging: {
    apiBaseUrl: 'https://cv-checker-api-staging.azurewebsites.net',
    appInsightsKey: process.env.VITE_APP_INSIGHTS_KEY,
    logLevel: 'info',
  },
  production: {
    apiBaseUrl: 'https://cv-checker-api.azurewebsites.net',
    appInsightsKey: process.env.VITE_APP_INSIGHTS_KEY,
    logLevel: 'error',
  },
};
```

**Priority:** P1 (Should Have)

---

### TECH-10: Development Workflow

#### TECH-10.1: Local Development Setup
**Requirements:**
- **Prerequisites:**
  - Node.js 18+ and npm 9+
  - Git
  - VS Code (recommended) with extensions:
    - ESLint
    - Prettier
    - TypeScript and JavaScript Language Features
    - Vite (optional)
- **Setup Steps:**
  ```bash
  # 1. Clone repository
  git clone <repo-url>
  cd cv-checker/frontend
  
  # 2. Install dependencies
  npm install
  
  # 3. Copy environment template
  cp .env.example .env.local
  
  # 4. Edit .env.local with local backend URL
  # VITE_API_BASE_URL=http://localhost:8000
  
  # 5. Start development server
  npm run dev
  
  # 6. Open browser to http://localhost:5173
  ```
- **Backend Dependency:**
  - Frontend requires backend running at `http://localhost:8000`
  - Start backend first: `cd backend && uvicorn app.main:app --reload`
  - Verify backend health: `curl http://localhost:8000/api/v1/health`

**Priority:** P0 (Must Have)

---

#### TECH-10.2: Code Quality Tools
**Requirements:**
- **ESLint Configuration:**
  - Extends: `eslint:recommended`, `plugin:@typescript-eslint/recommended`, `plugin:react-hooks/recommended`
  - Rules: Enforce consistent code style, prevent common bugs
  - Auto-fix on save (VS Code)
- **Prettier Configuration:**
  - Single quotes, 2-space indent, trailing commas
  - Integrated with ESLint (no conflicts)
  - Format on save (VS Code)
- **TypeScript Configuration:**
  - Strict mode enabled
  - `noImplicitAny`, `strictNullChecks`, `noUnusedLocals`
  - Path aliases: `@/` → `src/`
- **Pre-commit Hooks (Husky + lint-staged):**
  - Run ESLint on staged files
  - Run Prettier on staged files
  - Run type checking
  - Prevent commits with errors

**Priority:** P1 (Should Have)

---

### TECH-11: Monitoring & Observability

#### TECH-11.1: Application Insights Dashboard
**Requirements:**
- **Key Metrics Dashboard:**
  - User engagement: Daily active users, analysis completion rate
  - Performance: Page load time (p50, p95), API latency
  - Errors: Error rate by type, affected user percentage
  - Usage: Most common errors, popular workflows
- **Alerts:**
  - Error rate >5% → Email/Slack notification
  - API latency p95 >5s → Alert
  - Failed deployments → Alert
- **Custom Events to Track:**
  - `page_view` - Page URL, referrer
  - `cv_uploaded` - File size, upload duration
  - `analysis_started` - Timestamp
  - `analysis_completed` - Score, duration
  - `analysis_failed` - Error type, message
  - `recommendation_viewed` - Recommendation text (hashed)

**Priority:** P1 (Should Have)

---

#### TECH-11.2: Error Tracking & Debugging
**Requirements:**
- **Source Map Upload:**
  - Upload source maps to Azure for stack trace resolution
  - Keep source maps private (not served to users)
- **Error Context Capture:**
  - User agent, viewport size, timestamp
  - Last 10 user actions (breadcrumbs)
  - Application state at time of error (sanitized - no PII)
  - Network requests (URLs, status codes, durations)
- **Error Severity Levels:**
  - Critical: App crashes, data loss
  - High: Feature broken, API failures
  - Medium: UI glitches, non-critical errors
  - Low: Warnings, deprecations

**Priority:** P1 (Should Have)

---

### TECH-12: Frontend-Backend Contract Validation

#### TECH-12.1: API Contract Testing
**Requirements:**
- **OpenAPI Spec Validation:**
  - Frontend CI validates requests against backend OpenAPI spec
  - Detect breaking changes before deployment
  - Use tools: `openapi-validator`, `jest-openapi`
- **Mock Server for Testing:**
  - Use MSW (Mock Service Worker) with OpenAPI spec
  - Generate mock responses matching backend contract
  - Test frontend without running backend
- **Version Compatibility:**
  - Frontend checks backend `/api/v1/health` for version
  - Warn if backend version incompatible (e.g., major version mismatch)
  - Display user-friendly message: "Please refresh the page to update the app."

**Example Contract Test:**
```typescript
import { validateAgainstSpec } from 'jest-openapi';
import openapiSpec from './openapi.json';

validateAgainstSpec(openapiSpec);

test('analyze request matches OpenAPI spec', () => {
  const request = {
    cv_markdown: '# Test CV',
    job_description: 'Test job description',
  };
  expect(request).toSatisfySchemaInApiSpec('AnalyzeRequest');
});
```

**Priority:** P1 (Should Have)

---

#### TECH-12.2: Type Safety Across Layers
**Requirements:**
- **Shared Type Definitions:**
  - Generate TypeScript types from backend Pydantic models
  - Use `openapi-typescript` to create types from OpenAPI spec
  - Import types in frontend: `import type { AnalyzeResponse } from '@/api/generated'`
- **Runtime Validation:**
  - Validate API responses at runtime (optional, using Zod or io-ts)
  - Catch schema drift early
  - Log validation errors to Application Insights
- **Type-Safe API Client:**
  - Generated client provides full TypeScript IntelliSense
  - Compile-time errors for incorrect API usage

**Priority:** P1 (Should Have)

---

### TECH-13: Tabbed Analysis Report Implementation

#### TECH-13.1: State Management for Tabs
**Requirements:**
- **Application State:**
  - Add `activeTab` field to global state or component state
  - Type: `'cv' | 'job' | 'results'`
  - Default value: `'results'`
  - State management using Zustand, Context API, or AG-UI recommended pattern
- **Session Persistence:**
  - Store active tab in `sessionStorage` with key `cv-checker:active-tab`
  - Save tab state on every tab switch
  - Restore tab state on component mount
  - Clear tab state on session end (optional)
- **State Actions:**
  - `setActiveTab(tab)` - Update active tab
  - `getActiveTab()` - Retrieve current active tab
  - `resetActiveTab()` - Reset to default ('results')

**Example State Management (Zustand):**
```typescript
interface TabState {
  activeTab: 'cv' | 'job' | 'results';
  setActiveTab: (tab: 'cv' | 'job' | 'results') => void;
}

const useTabStore = create<TabState>((set) => ({
  activeTab: 'results',
  setActiveTab: (tab) => {
    set({ activeTab: tab });
    sessionStorage.setItem('cv-checker:active-tab', tab);
  },
}));
```

**Priority:** P0 (Must Have)

---

#### TECH-13.2: Markdown Rendering Libraries
**Requirements:**
- **Core Library:** `react-markdown` ✅ **APPROVED**
  - Install: `npm install react-markdown`
  - Converts Markdown to React components
  - Type-safe, actively maintained
  - Decision approved for production use
- **GitHub Flavored Markdown Support:** `remark-gfm` ✅ **APPROVED**
  - Install: `npm install remark-gfm`
  - Adds support for tables, strikethrough, task lists, autolinks
  - Use as plugin for react-markdown
  - Decision approved for production use
- **XSS Protection:** `rehype-sanitize` ✅ **APPROVED**
  - Install: `npm install rehype-sanitize`
  - Sanitizes HTML output to prevent XSS attacks
  - Removes dangerous tags and attributes
  - Use as rehype plugin for react-markdown
  - Decision approved for production use
- **Syntax Highlighting (Optional):** `react-syntax-highlighter`
  - Install: `npm install react-syntax-highlighter`
  - Highlight code blocks if present in CV
  - Improves readability of technical CVs

**Example Usage:**
```typescript
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';

<ReactMarkdown
  remarkPlugins={[remarkGfm]}
  rehypePlugins={[rehypeSanitize]}
>
  {cvMarkdown}
</ReactMarkdown>
```

**Security Configuration:**
- Configure `rehype-sanitize` schema to allow only safe elements:
  - Allow: headings, paragraphs, lists, links, code blocks, tables
  - Disallow: script, iframe, object, embed, form, input
  - Sanitize attributes: remove event handlers (onclick, onerror, etc.)

**Priority:** P0 (Must Have)

---

#### TECH-13.3: Tab Component Implementation
**Requirements:**
- **Component Structure:**
  ```typescript
  <TabbedResults>
    <TabList>
      <Tab id="cv" label="CV Document" />
      <Tab id="job" label="Job Description" />
      <Tab id="results" label="Analysis Results" />
    </TabList>
    <TabPanels>
      <TabPanel id="cv">
        <CVDocumentView content={cvMarkdown} />
      </TabPanel>
      <TabPanel id="job">
        <JobDescriptionView content={jobDescription} source={source} />
      </TabPanel>
      <TabPanel id="results">
        <ResultsDisplay analysis={analysisResult} />
      </TabPanel>
    </TabPanels>
  </TabbedResults>
  ```
- **Tab Accessibility:**
  - Use semantic HTML: `<div role="tablist">`, `<button role="tab">`, `<div role="tabpanel">`
  - ARIA attributes:
    - `aria-selected="true"` on active tab
    - `aria-controls="panel-id"` linking tab to panel
    - `aria-labelledby="tab-id"` on panel
    - `aria-hidden="true"` on inactive panels
  - Keyboard event handlers:
    - `onKeyDown` for Arrow keys, Enter, Space
    - Focus management with `useRef` and `focus()`
- **Styling:**
  - Use AG-UI theme tokens for consistent styling
  - Active tab: Underline or border-bottom (3px), primary color
  - Inactive tabs: Neutral color, no underline
  - Hover state (desktop): Subtle background change
  - Focus state: Visible outline (2px, high contrast)
  - Responsive: Adjust tab width and padding for mobile

**Example Tab Styling (CSS/TailwindCSS):**
```css
.tab {
  padding: 12px 24px;
  border-bottom: 3px solid transparent;
  color: var(--neutral-color);
  cursor: pointer;
}

.tab-active {
  border-bottom-color: var(--primary-color);
  color: var(--primary-color);
  font-weight: 600;
}

.tab:hover {
  background-color: var(--neutral-light);
}

.tab:focus {
  outline: 2px solid var(--focus-color);
  outline-offset: -2px;
}
```

**Priority:** P0 (Must Have)

---

#### TECH-13.4: Lazy Rendering & Performance
**Requirements:**
- **Conditional Rendering:**
  - Only render active tab content initially
  - Render other tabs on first activation (lazy load)
  - Cache rendered tabs to avoid re-rendering
  - Use React state to track which tabs have been rendered
- **Implementation Pattern:**
  ```typescript
  const [renderedTabs, setRenderedTabs] = useState<Set<string>>(new Set(['results']));
  
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    setRenderedTabs(prev => new Set(prev).add(tab));
  };
  
  return (
    <TabPanels>
      {(renderedTabs.has('cv') || activeTab === 'cv') && (
        <TabPanel id="cv" hidden={activeTab !== 'cv'}>
          <CVDocumentView content={cvMarkdown} />
        </TabPanel>
      )}
      {/* Similar for other tabs */}
    </TabPanels>
  );
  ```
- **Markdown Memoization:**
  - Use `React.useMemo()` to cache parsed Markdown
  - Dependency: `cvMarkdown` or `jobDescription` content
  - Prevents re-parsing on tab switches
  - Example:
    ```typescript
    const renderedCV = useMemo(() => (
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
      >
        {cvMarkdown}
      </ReactMarkdown>
    ), [cvMarkdown]);
    ```
- **Component Memoization:**
  - Wrap tab panels in `React.memo()` to prevent unnecessary re-renders
  - Only re-render when content or active state changes
- **Performance Monitoring:**
  - Measure tab switch time using Performance API
  - Log to Application Insights if >200ms
  - Custom event: `tab_switch_performance` with duration

**Priority:** P1 (Should Have)

---

#### TECH-13.5: Responsive Tab Behavior
**Requirements:**
- **Breakpoint Detection:**
  - Use CSS media queries or `window.matchMedia()` to detect screen size
  - Breakpoints:
    - Mobile: 320-767px
    - Tablet: 768-1023px
    - Desktop: 1024px+
- **Mobile Implementation Options:**
  - **Option 1 (Recommended):** Horizontal scrollable tabs
    - Use `overflow-x: auto` on tab container
    - Scroll active tab into view with `scrollIntoView()`
    - Show fade indicators if tabs overflow
    - CSS:
      ```css
      .tab-list-mobile {
        display: flex;
        overflow-x: auto;
        scrollbar-width: none; /* Hide scrollbar */
      }
      ```
  - **Option 2:** Dropdown selector
    - Replace tab bar with dropdown button
    - Click to show menu with all tabs
    - Select tab from menu
    - Requires additional component logic
- **Tab Label Adaptation:**
  - Desktop: Full labels ("CV Document", "Job Description", "Analysis Results")
  - Tablet: Shortened labels ("CV Document", "Job Desc", "Results")
  - Mobile: Icons + short labels or icons only (optional)
  - Use CSS media queries or conditional rendering
- **Touch Target Sizing:**
  - Mobile: Minimum 44x44px per tab
  - Tablet: Minimum 40x40px per tab
  - Desktop: 120px+ width recommended
  - Adequate padding and spacing

**Priority:** P0 (Must Have)

---

#### TECH-13.6: Testing Requirements
**Requirements:**
- **Unit Tests:**
  - Tab state management (setActiveTab, getActiveTab)
  - Session storage persistence (save/restore active tab)
  - Keyboard navigation handlers
  - Markdown rendering (XSS protection with rehype-sanitize)
- **Integration Tests:**
  - Tab switching updates active tab state
  - Active tab content displays, inactive tabs hidden
  - Tab state persists across component re-mounts
  - Markdown content renders correctly
- **Accessibility Tests:**
  - ARIA attributes correct (aria-selected, aria-controls, etc.)
  - Keyboard navigation works (Arrow keys, Enter, Space)
  - Screen reader announces tab changes
  - Focus indicators visible
  - axe-core: 0 violations
- **E2E Tests (Playwright/Cypress):**
  - User can click each tab and see content
  - Active tab visual indicator updates
  - Tab state persists on page reload
  - Tabs work on mobile, tablet, desktop viewports
  - Markdown content safe (no XSS)
- **Performance Tests:**
  - Tab switch time <100ms
  - Markdown parsing time <50ms for typical CV
  - Memory usage reasonable for large documents

**Example Test (Jest + Testing Library):**
```typescript
test('user can switch between tabs', () => {
  render(<TabbedResults analysis={mockAnalysis} cv={mockCV} job={mockJob} />);
  
  // Initially on Results tab
  expect(screen.getByRole('tab', { name: 'Analysis Results' })).toHaveAttribute('aria-selected', 'true');
  expect(screen.getByRole('tabpanel', { name: 'Analysis Results' })).toBeVisible();
  
  // Switch to CV tab
  fireEvent.click(screen.getByRole('tab', { name: 'CV Document' }));
  expect(screen.getByRole('tab', { name: 'CV Document' })).toHaveAttribute('aria-selected', 'true');
  expect(screen.getByRole('tabpanel', { name: 'CV Document' })).toBeVisible();
  expect(screen.getByRole('tabpanel', { name: 'Analysis Results' })).not.toBeVisible();
});
```

**Priority:** P0 (Must Have)

---

## Acceptance Criteria

### AC-FE1: Core Workflow (Phase 2 - Week 7-8)

**AC-FE1.1: CV Upload**
- [ ] User can click "Choose File" or drag-and-drop Markdown file
- [ ] File validation: only .md files up to 2MB accepted
- [ ] Clear error messages for invalid files
- [ ] Success confirmation displays filename and size
- [ ] Uploaded file content stored in state

**AC-FE1.2: Job Description Input**
- [ ] User can paste job description into textarea
- [ ] Character counter updates in real-time (current / 50,000)
- [ ] Validation: minimum 100 characters, maximum 50,000 characters
- [ ] Clear button empties textarea
- [ ] Input preserved on navigation (session persistence)

**AC-FE1.3: Analysis Trigger**
- [ ] "Analyze Match" button disabled until both CV and job provided
- [ ] Button click triggers API call with CV and job data
- [ ] Loading state shows spinner and status messages
- [ ] Analysis completes within 30 seconds (normal conditions)
- [ ] Results displayed automatically upon completion

**AC-FE1.4: Error Handling**
- [ ] Network errors show user-friendly message
- [ ] API errors show specific error message
- [ ] Timeout errors (>60s) show timeout message
- [ ] "Retry" button allows re-attempting failed analysis
- [ ] User input preserved after error

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1, AC2.2

---

### AC-FE2: Results Visualization (Phase 2 - Week 8-9)

**AC-FE2.1: Score Display**
- [ ] Overall score (1-100) prominently displayed
- [ ] Visual indicator (gauge/progress circle) matches score
- [ ] Color coding: Red <50, Yellow 50-74, Green 75+
- [ ] Interpretive label (Poor/Fair/Good/Excellent Match)
- [ ] Summary statement (2-3 sentences) explains score

**AC-FE2.2: Subscores Breakdown**
- [ ] Four subscores displayed: Skills, Experience, Keywords, Education
- [ ] Each subscore shown with progress bar and numeric value
- [ ] Tooltip on hover/tap explains each subscore
- [ ] Color coding consistent with overall score
- [ ] Expandable details for each subscore (optional)

**AC-FE2.3: Recommendations Display**
- [ ] Minimum 5 recommendations shown
- [ ] Recommendations categorized (Add, Modify, Emphasize, Remove)
- [ ] Priority indicators (High, Medium, Low) visible
- [ ] Expandable cards show full details (rationale, example, impact)
- [ ] Filter/sort functionality works correctly
- [ ] High-priority recommendations appear first by default

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.3

---

### AC-FE3: Analysis History (Phase 2 - Week 9)

**AC-FE3.1: History List**
- [ ] User can access "Analysis History" view
- [ ] List shows past analyses with date, score, CV, job
- [ ] Sort by date (newest first) or score (highest first)
- [ ] Pagination: 10 results per page
- [ ] Empty state message when no history exists

**AC-FE3.2: View Past Analysis**
- [ ] User can click on history entry to view full details
- [ ] Full analysis results displayed (same format as fresh analysis)
- [ ] Timestamp badge indicates this is past analysis
- [ ] "Back to History" navigation works

**Priority:** P1 (Should Have)  
**Related PRD:** AC2.4

---

### AC-FE4: Responsive Design (Phase 2 - Week 9-10)

**AC-FE4.1: Mobile (320px - 767px)**
- [ ] Single-column layout on mobile devices
- [ ] All interactive elements have minimum 44x44px touch targets
- [ ] No horizontal scrolling required
- [ ] Upload and input interfaces optimized for mobile
- [ ] Results readable without pinch-zoom

**AC-FE4.2: Tablet (768px - 1023px)**
- [ ] Two-column layout where appropriate
- [ ] Touch targets minimum 40x40px
- [ ] Optimized use of screen space
- [ ] All features accessible and usable

**AC-FE4.3: Desktop (1024px+)**
- [ ] Multi-column layout maximizes space
- [ ] Hover interactions enhance experience
- [ ] Keyboard navigation fully functional
- [ ] All features accessible via keyboard

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1

---

### AC-FE5: Accessibility (Phase 2 - Week 9-10)

**AC-FE5.1: Keyboard Navigation**
- [ ] All interactive elements accessible via Tab key
- [ ] Visible focus indicators (2px outline minimum)
- [ ] Logical tab order throughout application
- [ ] No keyboard traps
- [ ] Enter key submits forms, Esc closes modals

**AC-FE5.2: Screen Reader Compatibility**
- [ ] All images have descriptive alt text
- [ ] Form inputs have explicit labels
- [ ] Dynamic content changes announced (ARIA live regions)
- [ ] Semantic HTML structure (headings, landmarks)
- [ ] Tested with NVDA (Windows) and VoiceOver (macOS/iOS)

**AC-FE5.3: Color & Contrast**
- [ ] All text meets WCAG AA contrast ratios (4.5:1 normal, 3:1 large)
- [ ] UI components meet 3:1 contrast ratio
- [ ] Information not conveyed by color alone
- [ ] Verified with automated tools (axe, WAVE)

**AC-FE5.4: Text Scaling**
- [ ] Content readable at 200% browser zoom
- [ ] No horizontal scrolling at 200% zoom
- [ ] Text reflows appropriately
- [ ] Relative font sizing (rem/em) used

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.1

---

### AC-FE6: Usability Testing (Phase 2 - Week 10)

**AC-FE6.1: User Testing**
- [ ] 5+ representative users complete full workflow
- [ ] Task success rate >90% (upload CV, input job, view results)
- [ ] Average time to first analysis <5 minutes
- [ ] Users can interpret results without guidance
- [ ] Users identify high-priority recommendations correctly

**AC-FE6.2: User Satisfaction**
- [ ] Post-test survey score ≥4/5
- [ ] Users report interface as "easy to use" or "very easy to use"
- [ ] Users find recommendations "helpful" or "very helpful"
- [ ] Users would recommend tool to others (NPS >0)

**Priority:** P0 (Must Have)  
**Related PRD:** AC2.5

---

### AC-FE7: Tabbed Analysis Report Interface (Phase 2 - Week 8-9)

**AC-FE7.1: Tab Navigation**
- [ ] Three tabs are displayed: "CV Document", "Job Description", "Analysis Results"
- [ ] User can switch between all three tabs by clicking/tapping
- [ ] Active tab is clearly indicated with visual styling (underline, color, or background)
- [ ] Inactive tabs are visually distinct from active tab
- [ ] Default tab is "Analysis Results" when analysis completes
- [ ] Tab state persists when switching between tabs during session
- [ ] Tab state restored on page reload (via sessionStorage)

**AC-FE7.2: Keyboard Navigation**
- [ ] User can navigate between tabs using Arrow keys (←/→)
- [ ] Tab key moves focus to tabs, then into tab content
- [ ] Enter or Space key activates the focused tab
- [ ] Focus indicators are visible and meet WCAG AA contrast requirements
- [ ] All tabs are keyboard accessible with no keyboard traps

**AC-FE7.3: CV Document Tab**
- [ ] Uploaded CV renders correctly with Markdown formatting
- [ ] Headings, lists, code blocks, and links display properly
- [ ] Professional styling applied (consistent with AG-UI theme)
- [ ] XSS protection: No malicious content executes (sanitized with rehype-sanitize)
- [ ] "No CV available" message displays when no CV uploaded
- [ ] Content scrolls independently within tab panel
- [ ] Large CVs (2MB) render without performance issues

**AC-FE7.4: Job Description Tab**
- [ ] Job description displays with proper formatting
- [ ] Source indicator shows "Manually entered" for user-pasted jobs
- [ ] Markdown job descriptions render correctly (if applicable)
- [ ] Plain text job descriptions display with line breaks preserved
- [ ] "No job description available" message displays when empty
- [ ] Long job descriptions are scrollable without truncation
- [ ] XSS protection: Content is sanitized

**AC-FE7.5: Analysis Results Tab**
- [ ] All existing results content displays correctly in tab
- [ ] Overall score gauge/indicator renders properly
- [ ] Subscores breakdown shows all four scores
- [ ] Strengths and gaps display correctly
- [ ] Recommendations list functions as before (expandable, filterable)
- [ ] All interactive elements work (tooltips, expand/collapse, filters)
- [ ] Scroll behavior is independent from other tabs

**AC-FE7.6: Responsive Design**
- [ ] Desktop (1024px+): Horizontal tabs with full labels
- [ ] Tablet (768-1023px): Tabs work with condensed labels if needed
- [ ] Mobile (320-767px): Tabs are scrollable or dropdown, touch-friendly
- [ ] Minimum touch target size met: 44x44px on mobile, 40x40px on tablet
- [ ] Tab labels adapt appropriately on smaller screens (e.g., "CV Document" → "CV")
- [ ] All tabs accessible and functional on all screen sizes

**AC-FE7.7: Performance**
- [ ] Tab switching responds in <100ms (smooth, no lag)
- [ ] Only active tab content renders initially (lazy rendering)
- [ ] Markdown content caches to avoid re-parsing on tab revisit
- [ ] No flash of unstyled content during tab switch
- [ ] Memory usage remains reasonable for large documents
- [ ] Tab switching performance logged to Application Insights

**AC-FE7.8: Accessibility**
- [ ] Tabs use proper ARIA roles: `tablist`, `tab`, `tabpanel`
- [ ] `aria-selected="true"` on active tab
- [ ] `aria-controls` links tab to panel
- [ ] `aria-labelledby` on panel references tab
- [ ] Screen reader announces active tab and content changes
- [ ] Color is not the only indicator of active tab (uses underline/border/icon)
- [ ] Passes automated accessibility testing (axe-core, 0 violations)

**Priority:** P0 (Must Have)  
**Related PRD:** Feature 4B, AC2.1, AC2.3

---

## Out of Scope

The following features are **NOT included** in Phase 2 frontend implementation:

### Phase 2 Exclusions

1. **User Authentication & Accounts**
   - No login/registration
   - No user profiles
   - Session-based usage only (local storage)
   - No password management

2. **Multi-CV Management**
   - No saving multiple CVs per user
   - One CV at a time per session
   - No CV version comparison

3. **Advanced Visualizations**
   - No score improvement charts/graphs
   - No industry benchmarking
   - No comparison between multiple analyses (side-by-side)

4. **Export Features**
   - No PDF export of analysis
   - No JSON download
   - No print-optimized view
   - No email sharing

5. **Collaboration Features**
   - No sharing analyses with others
   - No comments or annotations
   - No team/coach access

6. **CV Editing**
   - No in-app CV editor
   - No CV template generation
   - No automated CV rewriting
   - Recommendations only (user implements externally)

7. **Job Description Enhancements**
   - No LinkedIn URL scraping (manual paste only)
   - No job board integration
   - No saved job templates

8. **Advanced Analysis Features**
   - No AI chatbot for Q&A about results
   - No interview question preparation
   - No salary expectation guidance
   - No company culture fit analysis

9. **Offline Mode**
   - No offline analysis capability
   - Requires internet connection

10. **Mobile Apps**
    - No native iOS/Android apps
    - Web-only (responsive design)

11. **Notifications**
    - No email notifications
    - No push notifications
    - No reminder system

12. **Internationalization**
    - English only
    - No multi-language support
    - No currency/date localization

---

### Future Consideration (Phase 3+)

These features may be prioritized after Phase 2 based on user feedback:

- User accounts and authentication (Microsoft/LinkedIn/Google SSO)
- CV version management and comparison
- Export to PDF/JSON
- Analysis sharing via unique URLs
- Score improvement tracking over time
- Industry benchmarking
- Interview preparation module
- Browser extension for job boards
- Mobile native apps
- Multi-language support

---

## Success Metrics

### User Engagement Metrics

**UE-1: Workflow Completion Rate**
- **Target:** 70% of users who upload a CV complete at least one analysis
- **Measurement:** Track (uploads / analyses completed) ratio
- **Tracking:** Google Analytics or Azure Application Insights events

**UE-2: Time to First Analysis**
- **Target:** <5 minutes average from landing to viewing results
- **Measurement:** Time between page load and analysis completion
- **Tracking:** Performance timing API + analytics

**UE-3: Repeat Usage**
- **Target:** 40% of users perform 3+ analyses within first visit
- **Measurement:** Count analyses per session (local storage ID)
- **Tracking:** Analytics session tracking

---

### User Experience Metrics

**UX-6: Task Success Rate**
- **Target:** >90% of usability test participants complete all tasks
- **Tasks:**
  1. Upload CV
  2. Input job description
  3. Trigger analysis
  4. Interpret overall score
  5. Identify top recommendation
- **Measurement:** Usability testing observations
- **Frequency:** Pre-launch + quarterly

**UX-7: User Satisfaction**
- **Target:** Average satisfaction score ≥4/5
- **Measurement:** Post-analysis survey (1-5 scale)
- **Questions:**
  - How easy was it to upload your CV?
  - How clear were the analysis results?
  - How helpful were the recommendations?
  - How likely are you to use this tool again?
- **Frequency:** Optional survey after each analysis

**UX-8: Error Recovery Rate**
- **Target:** <5% of analyses result in unrecoverable errors
- **Measurement:** (Failed analyses without retry) / (Total analyses attempted)
- **Tracking:** Error logs in Application Insights

---

### Technical Performance Metrics

**TECH-6: Page Load Performance**
- **Targets:**
  - First Contentful Paint <1.5s
  - Time to Interactive <3s
  - Largest Contentful Paint <2.5s
- **Measurement:** Lighthouse CI in GitHub Actions
- **Frequency:** Every production deployment

**TECH-7: API Response Time**
- **Target:** 
  - Analysis API p95 <30s
  - Other APIs p95 <500ms
- **Measurement:** Azure Application Insights
- **Alerts:** Trigger if p95 exceeds threshold

**TECH-8: Client-Side Error Rate**
- **Target:** <1% of user sessions encounter JavaScript errors
- **Measurement:** (Sessions with errors) / (Total sessions)
- **Tracking:** Application Insights client-side logging
- **Alerts:** Spike detection (>5% error rate)

---

### Accessibility Metrics

**A11Y-1: WCAG Compliance**
- **Target:** 100% WCAG 2.1 AA compliance
- **Measurement:** Automated testing (axe, Lighthouse)
- **Frequency:** Every pull request (CI/CD)

**A11Y-2: Keyboard Navigation Coverage**
- **Target:** 100% of interactive elements accessible via keyboard
- **Measurement:** Manual testing checklist
- **Frequency:** Before each release

**A11Y-3: Screen Reader Compatibility**
- **Target:** All critical workflows completable with screen reader
- **Measurement:** Manual testing with NVDA and VoiceOver
- **Frequency:** Before each major release

---

### Business Impact Metrics (Post-Launch)

**BI-1: Recommendation Implementation Rate**
- **Target:** 60% of users report implementing ≥3 recommendations
- **Measurement:** Follow-up survey (2 weeks post-analysis)
- **Frequency:** Monthly survey batch

**BI-2: Score Improvement**
- **Target:** 50% of users who re-analyze see score increase
- **Measurement:** Compare scores for same CV across analyses
- **Tracking:** Backend analytics (history comparison)

**BI-3: Net Promoter Score (NPS)**
- **Target:** NPS ≥40
- **Measurement:** "How likely are you to recommend CV Checker?" (0-10 scale)
- **Frequency:** Quarterly survey

---

## Appendix

### A. Wireframe References

(Note: Actual wireframes to be created by UX designer during implementation. References below describe expected screens.)

**Screen 1: Upload & Input**
- Header with logo and navigation
- Left panel: CV upload interface
- Right panel: Job description input
- Bottom: "Analyze Match" button (center, prominent)
- Footer: Links to help, privacy policy

**Screen 2: Loading State**
- Full-screen overlay with spinner
- Progress messages ("Parsing CV...", etc.)
- "Cancel" button (bottom)

**Screen 3: Results**
- Top: Overall score with gauge and summary
- Middle: Subscores breakdown (4 bars)
- Middle: Top 3 strengths and improvements
- Bottom: Full recommendations list (expandable cards)
- Sidebar: "New Analysis" and "View History" buttons

**Screen 4: Analysis History**
- List of past analyses (cards)
- Sort and filter controls
- Click on card to view full results
- "Back to New Analysis" button

---

### B. AG-UI Component Mapping

| Feature | AG-UI Component(s) |
|---------|-------------------|
| CV Upload | FileUpload, Button, Card |
| Job Input | Textarea, CharCounter, Button |
| Analyze Button | PrimaryButton, Spinner (loading) |
| Score Gauge | ProgressCircle, Badge, Typography |
| Subscores | ProgressBar, Tooltip, Flex |
| Recommendations | Card, Accordion, Badge, Icon |
| History List | DataTable or CardList, Pagination |
| Notifications | Toast, Alert |
| Modals | Dialog, Modal |

*(Note: Exact component names depend on AG-UI library documentation)*

---

### C. API Endpoints Used

From backend Phase 1 implementation (see [backend/README.md](../../backend/README.md)):

| Endpoint | Method | Purpose | Frontend Usage | Request Body | Response |
|----------|--------|---------|----------------|--------------|----------|
| `/api/v1/analyze` | POST | Analyze CV vs job | Analyze button action | `{cv_markdown: string, job_description: string}` | `AnalyzeResponse` (see below) |
| `/api/v1/health` | GET | Health check | App initialization, monitoring | None | `{status, version, service, azure_openai}` |
| `/api/v1/openapi.json` | GET | OpenAPI specification | Client generation | None | OpenAPI 3.0 JSON spec |

**⚠️ Important Backend Alignment Notes:**

1. **No separate CV/Job endpoints:** Unlike the table below suggests, the backend Phase 1 does NOT have separate `/api/v1/cvs` or `/api/v1/jobs` endpoints. Analysis is done in a single stateless call.

2. **No history endpoint yet:** `/api/v1/cvs/{cv_id}/analyses` does not exist in Phase 1. Frontend must manage history locally via localStorage.

3. **CosmosDB Storage:** Backend now stores CV, job description, and source information with each analysis in CosmosDB. These are returned in the analysis response for display consistency.

4. **Analysis Response Structure:**
```typescript
interface AnalyzeResponse {
  analysis_id: string;           // UUID for tracking
  cv_markdown: string;            // FULL CV content as submitted
  job_description: string;        // FULL job description as submitted
  source_type: 'manual' | 'linkedin_url';  // How job description was provided
  source_url?: string;            // Optional LinkedIn URL if scraped (Phase 3)
  overall_score: number;          // 0-100
  skill_matches: SkillMatch[];    // Detailed skill matching
  experience_match: object;       // Experience analysis (structure may vary)
  education_match: object;        // Education analysis (structure may vary)
  strengths: string[];            // Top strengths (plain strings)
  gaps: string[];                 // Identified gaps (plain strings)
  recommendations: string[];      // Action items (plain strings - no structure in Phase 1)
}

interface SkillMatch {
  skill_name: string;
  required: boolean;
  candidate_has: boolean;
  proficiency_level?: string;
  years_experience?: number;
  match_score: number;  // 0.0 to 1.0
}
```

5. **Frontend Responsibilities:**
- **History Management:** Store analysis results in localStorage (last 10)
- **Session Persistence:** Store current CV and job in localStorage
- **Client-Side Validation:** Enforce same rules as backend before API call
- **Graceful Degradation:** Handle missing fields in response (experience_match, education_match are objects with flexible schema)

**Future API Enhancements (Phase 3):**
- User authentication endpoints
- Persistent storage endpoints (save/retrieve CVs, jobs, analyses)
- Batch analysis endpoint
- Analysis comparison endpoint

---

### D. Localization Considerations (Future)

While Phase 2 is English-only, design with future localization in mind:

- Externalize all user-facing strings (i18n library)
- Avoid hardcoded text in components
- Use relative date/time formatting
- Design UI to accommodate text expansion (RTL languages can be 30% longer)
- Avoid text in images (use SVG icons)

---

### E. Browser Support

**Supported Browsers:**
- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

**Mobile Browsers:**
- Safari on iOS (latest 2 major versions)
- Chrome on Android (latest 2 versions)

**Not Supported:**
- Internet Explorer (any version)
- Browsers >2 years old

---

### F. Design Tokens (AG-UI Theme)

Key design tokens to configure:

```javascript
{
  colors: {
    primary: "#0078D4",      // Microsoft blue
    success: "#107C10",      // Green (75-100 score)
    warning: "#F7B500",      // Yellow (50-74 score)
    error: "#D13438",        // Red (0-49 score)
    neutral: "#323130",      // Text
    background: "#FFFFFF",   // Page background
  },
  typography: {
    fontFamily: "Segoe UI, sans-serif",
    fontSize: {
      small: "12px",
      medium: "14px",
      large: "16px",
      xlarge: "20px",
      xxlarge: "28px",
    },
  },
  spacing: {
    xs: "4px",
    sm: "8px",
    md: "16px",
    lg: "24px",
    xl: "32px",
  },
  borderRadius: "4px",
  shadows: {
    card: "0 2px 4px rgba(0,0,0,0.1)",
    modal: "0 4px 16px rgba(0,0,0,0.2)",
  }
}
```

---

### G. Testing Checklist

**Unit Testing:**
- [ ] CV upload validation logic
- [ ] Job description validation logic
- [ ] Score calculation display
- [ ] Recommendation filtering/sorting
- [ ] API client error handling

**Integration Testing:**
- [ ] Full upload → analyze → results flow
- [ ] History persistence and retrieval
- [ ] Error handling and retry logic

**E2E Testing (Playwright/Cypress):**
- [ ] Happy path: Upload CV → Input job → View results
- [ ] Error path: Invalid file, network error, timeout
- [ ] History path: View past analyses
- [ ] Responsive: Test on mobile, tablet, desktop viewports

**Accessibility Testing:**
- [ ] Keyboard navigation (Tab, Enter, Esc)
- [ ] Screen reader (NVDA, VoiceOver)
- [ ] Color contrast (automated tools)
- [ ] Text scaling (200% zoom)

**Performance Testing:**
- [ ] Lighthouse CI (performance, a11y, best practices)
- [ ] Load testing (simulate 100 concurrent users)
- [ ] Network throttling (slow 3G)

**Cross-Browser Testing:**
- [ ] Chrome, Firefox, Safari, Edge (latest 2 versions)
- [ ] iOS Safari, Android Chrome

**Usability Testing:**
- [ ] 5+ participants (representative of personas)
- [ ] Task-based scenarios
- [ ] Think-aloud protocol
- [ ] Post-test survey

---

### H. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-31 | Frontend Team | Initial FRD creation for Phase 2 |
| 1.1 | 2025-12-31 | Developer Lead | **Technical Review Complete**<br/>- Added comprehensive API integration requirements (TECH-2)<br/>- Documented backend contract alignment (single `/api/v1/analyze` endpoint)<br/>- Enhanced security requirements (file upload validation, XSS prevention, CSP)<br/>- Added detailed error handling strategies (API, network, timeout)<br/>- Specified testing requirements (unit, integration, E2E, a11y)<br/>- Added CI/CD pipeline configuration (GitHub Actions, quality gates)<br/>- Documented deployment strategy (Azure Static Web Apps, environments)<br/>- Added monitoring & observability (Application Insights, error tracking)<br/>- Clarified state management (localStorage for history, no backend storage)<br/>- Added performance optimization requirements (Core Web Vitals, Lighthouse CI)<br/>- Documented development workflow (local setup, code quality tools)<br/>- Added API contract validation (OpenAPI spec, type safety)<br/>- Flagged AG-UI framework validation requirement<br/>- Updated API endpoints table with accurate backend contract<br/>- Enhanced recommendations display with backend alignment notes |

---

**End of Document**
