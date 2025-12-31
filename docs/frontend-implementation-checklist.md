# Frontend Implementation Checklist

**Reference:** [Frontend AG-UI FRD v1.1](../specs/features/frontend-ag-ui.md)  
**Phase:** Phase 2 - Frontend Implementation (Weeks 7-10)  
**Last Updated:** December 31, 2025

---

## Pre-Implementation (Week 6)

### Framework Validation
- [ ] Verify AG-UI framework is available and documented
- [ ] If AG-UI not ready, choose fallback: Fluent UI 2 OR React + Radix UI
- [ ] Document framework choice in ADR
- [ ] Review framework component library coverage

### Backend Integration Prep
- [ ] Run backend locally: `cd backend && uvicorn app.main:app --reload`
- [ ] Test health endpoint: `curl http://localhost:8000/api/v1/health`
- [ ] Test analyze endpoint with sample data
- [ ] Download OpenAPI spec: `curl http://localhost:8000/api/v1/openapi.json > openapi.json`
- [ ] Review backend code:
  - [ ] `backend/app/main.py` (API endpoints)
  - [ ] `backend/app/models/requests.py` (request validation)
  - [ ] `backend/app/models/responses.py` (response structure)

### Repository Setup
- [ ] Create `frontend/` directory in repository
- [ ] Initialize project: `npm create vite@latest frontend -- --template react-ts`
- [ ] Set up Git: `.gitignore` for `node_modules/`, `.env.local`, `dist/`
- [ ] Create `.env.example`:
  ```env
  VITE_API_BASE_URL=http://localhost:8000
  VITE_APP_INSIGHTS_KEY=
  VITE_ENV=development
  ```

### CI/CD Setup
- [ ] Create `.github/workflows/frontend-ci.yml`
- [ ] Configure Azure Static Web Apps in Azure Portal
- [ ] Add GitHub secrets: `AZURE_STATIC_WEB_APPS_API_TOKEN`, `APP_INSIGHTS_KEY`
- [ ] Test deployment to preview environment

---

## Week 7: Core Workflow

### File Upload Component
- [ ] Create `FileUpload.tsx` component
- [ ] Implement drag-and-drop zone
- [ ] Add file picker button
- [ ] **SECURITY:** Validate file extension (`.md` only)
- [ ] **SECURITY:** Validate file size (max 2MB)
- [ ] **SECURITY:** Validate MIME type (`text/markdown` or `text/plain`)
- [ ] Show upload progress indicator
- [ ] Display success state (filename, size, timestamp)
- [ ] Add "Remove" button
- [ ] Write unit tests for validation logic

### Job Description Input
- [ ] Create `JobDescriptionInput.tsx` component
- [ ] Add multi-line textarea (min 10 rows)
- [ ] Add character counter (real-time, max 50,000)
- [ ] Validate min length (100 characters)
- [ ] Add "Clear" button
- [ ] **SECURITY:** Sanitize input (trim, normalize line endings, remove control chars)
- [ ] Persist to localStorage on change
- [ ] Write unit tests for sanitization

### API Client Setup
- [ ] Install OpenAPI generator: `npm install @openapitools/openapi-generator-cli`
- [ ] Generate TypeScript client:
  ```bash
  npx openapi-typescript-codegen --input openapi.json --output src/api/generated --client axios
  ```
- [ ] Create API service wrapper (`src/api/cvChecker.ts`)
- [ ] Configure axios interceptors (add headers, handle errors)
- [ ] Set timeout: 60s for analyze, 10s for health
- [ ] Write unit tests with MSW (Mock Service Worker)

### Analyze Workflow
- [ ] Create `AnalyzeButton.tsx` component
- [ ] Disable button until CV and job are provided
- [ ] Show loading state during analysis (spinner + status messages)
- [ ] Handle API errors (400, 422, 500, timeout, network)
- [ ] Display user-friendly error messages
- [ ] Add "Retry" button on error
- [ ] Store analysis result in state
- [ ] Write integration test for full workflow

### State Management
- [ ] Choose state library: AG-UI approach OR Zustand OR React Context
- [ ] Create store with:
  - `currentCv: { filename, content, uploadedAt }`
  - `currentJob: { description, lastModified }`
  - `currentAnalysis: { isLoading, error, result }`
  - `analysisHistory: AnalyzeResponse[]`
- [ ] Implement actions: `uploadCV`, `updateJob`, `startAnalysis`, `completeAnalysis`, `failAnalysis`
- [ ] Persist to localStorage (namespace: `cv-checker:*`)
- [ ] Write unit tests for state logic

---

## Week 8: Results Visualization

### Overall Score Display
- [ ] Create `OverallScore.tsx` component
- [ ] Display score (0-100) with large font (48-72px)
- [ ] Add visual gauge/progress circle
- [ ] Color coding: Red <50, Yellow 50-74, Green 75+
- [ ] Show interpretive label (Poor/Fair/Good/Excellent Match)
- [ ] Add 2-3 sentence summary
- [ ] Ensure accessibility (ARIA labels, sufficient contrast)
- [ ] Write unit tests for score formatting

### Subscores Breakdown
- [ ] Create `SubscoresBreakdown.tsx` component
- [ ] Display 4 subscores: Skills, Experience, Keywords, Education
- [ ] Add horizontal progress bars
- [ ] Show numeric values (out of 100)
- [ ] Add tooltips with explanations
- [ ] Color coding consistent with overall score
- [ ] Write unit tests for rendering

### Strengths & Gaps
- [ ] Create `StrengthsGaps.tsx` component
- [ ] Display top 3 strengths (bullet list with ✓ icons)
- [ ] Display top 3 gaps (bullet list with ⚠️ icons)
- [ ] Link to detailed recommendations
- [ ] Ensure accessibility (semantic HTML, ARIA)

### Recommendations List
- [ ] Create `RecommendationsList.tsx` component
- [ ] Display recommendations as cards
- [ ] **IMPORTANT:** Handle simple string[] from backend (Phase 1 limitation)
- [ ] Auto-infer priority: first 3 = High, next 3 = Medium, rest = Low
- [ ] Add filter/sort controls (by priority, by category)
- [ ] Make cards expandable (future: show rationale, example)
- [ ] Use virtualization if >20 recommendations (react-window)
- [ ] Write unit tests for filtering/sorting

---

## Week 9: History & Polish

### Analysis History
- [ ] Create `AnalysisHistory.tsx` component
- [ ] Display list of past analyses (cards or table)
- [ ] Show: date, score, CV filename, job title (if extractable)
- [ ] Add sort options (by date, by score)
- [ ] Implement pagination (10 per page)
- [ ] Add "View Details" action
- [ ] Store in localStorage (max 10, auto-cleanup after 7 days)
- [ ] Handle quota exceeded (show warning, auto-delete oldest)
- [ ] Add empty state ("No analyses yet")
- [ ] Write integration tests

### Responsive Design
- [ ] Test on mobile (320px-767px)
  - [ ] Single-column layout
  - [ ] Touch targets 44x44px minimum
  - [ ] No horizontal scrolling
- [ ] Test on tablet (768px-1023px)
  - [ ] Two-column layout
  - [ ] Touch targets 40x40px minimum
- [ ] Test on desktop (1024px+)
  - [ ] Multi-column layout
  - [ ] Keyboard navigation
  - [ ] Hover interactions

### Error Handling
- [ ] Implement React Error Boundary (top-level)
- [ ] Add component-level boundaries for major sections
- [ ] Create fallback UI ("Something went wrong" + Refresh button)
- [ ] Log errors to Application Insights
- [ ] Capture error context (user agent, breadcrumbs, state)
- [ ] Test error scenarios

### Application Insights
- [ ] Install: `npm install @microsoft/applicationinsights-web`
- [ ] Initialize with instrumentation key
- [ ] Enable auto-collection (page views, AJAX, exceptions)
- [ ] Add custom events:
  - [ ] `cv_uploaded` (file size, duration)
  - [ ] `analysis_started`
  - [ ] `analysis_completed` (score, duration)
  - [ ] `analysis_failed` (error type)
- [ ] **IMPORTANT:** Log metadata only, NO PII, NO CV content
- [ ] Test logging in development

---

## Week 10: Testing & Deployment

### Unit Tests
- [ ] Achieve >80% coverage for:
  - [ ] Utility functions (validation, sanitization, formatting)
  - [ ] State management (actions, selectors)
  - [ ] API client (mock with MSW)
- [ ] Run tests: `npm test -- --coverage`
- [ ] Add coverage report to CI/CD

### Integration Tests
- [ ] Test full workflows:
  - [ ] Upload CV → Enter job → Analyze → View results
  - [ ] View history → Select analysis → View details
  - [ ] Upload invalid file → See error message
  - [ ] API timeout → See retry button
- [ ] Use Testing Library: `@testing-library/react`
- [ ] Mock API with MSW
- [ ] Mock localStorage

### E2E Tests
- [ ] Install Playwright: `npm install -D @playwright/test`
- [ ] Create test specs:
  - [ ] `e2e/analyze-workflow.spec.ts` (happy path)
  - [ ] `e2e/error-handling.spec.ts` (error scenarios)
  - [ ] `e2e/responsive.spec.ts` (mobile, tablet, desktop)
- [ ] Run against staging environment
- [ ] Add to CI/CD (run on every PR)

### Accessibility Tests
- [ ] Install axe-core: `npm install -D @axe-core/playwright`
- [ ] Add automated a11y tests to E2E suite
- [ ] Manual testing:
  - [ ] Keyboard navigation (Tab, Enter, Esc)
  - [ ] Screen reader (NVDA on Windows, VoiceOver on macOS)
  - [ ] Color contrast (WebAIM Contrast Checker)
  - [ ] Text scaling (200% zoom)
- [ ] Fix all WCAG AA violations

### Performance Testing
- [ ] Install Lighthouse CI: `npm install -D @lhci/cli`
- [ ] Create `lighthouserc.json` config
- [ ] Set thresholds: Performance >90, Accessibility >95, Best Practices >90
- [ ] Add to CI/CD (fail if thresholds not met)
- [ ] Optimize if needed:
  - [ ] Code splitting (lazy load routes)
  - [ ] Image optimization
  - [ ] Critical CSS inlining

### Security Audit
- [ ] Run `npm audit` (fix critical vulnerabilities)
- [ ] Review dependencies (remove unused, minimize count)
- [ ] Configure CSP headers in `staticwebapp.config.json`:
  ```json
  {
    "globalHeaders": {
      "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://js.monitor.azure.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://*.azurewebsites.net https://dc.services.visualstudio.com;"
    }
  }
  ```
- [ ] Review all user input handling (file upload, textarea)
- [ ] Ensure no `dangerouslySetInnerHTML` usage

### Deployment
- [ ] Test preview deployment (on PR)
- [ ] Verify environment variables (API URL, App Insights key)
- [ ] Test against staging backend
- [ ] Manual smoke test on preview URL
- [ ] Merge to main → Deploy to production
- [ ] Monitor Application Insights for errors
- [ ] Test production deployment

---

## Post-Deployment

### Monitoring
- [ ] Set up Application Insights dashboard
  - [ ] User engagement: DAU, analysis completion rate
  - [ ] Performance: Page load time (p50, p95), API latency
  - [ ] Errors: Error rate, top errors
- [ ] Configure alerts:
  - [ ] Error rate >5% → Email/Slack
  - [ ] API latency p95 >5s → Alert
  - [ ] Failed deployments → Alert

### Documentation
- [ ] Create `frontend/README.md`:
  - [ ] Setup instructions
  - [ ] Environment variables
  - [ ] Development commands (`npm run dev`, `npm test`, `npm run build`)
  - [ ] Deployment process
- [ ] Update architecture diagrams with frontend components
- [ ] Document API integration patterns
- [ ] Create troubleshooting guide

---

## Quality Gates (All Must Pass)

### Code Quality
- ✅ ESLint: No errors
- ✅ TypeScript: No type errors
- ✅ Prettier: All files formatted
- ✅ Pre-commit hooks: Working

### Testing
- ✅ Unit tests: 100% passing, >80% coverage
- ✅ Integration tests: All passing
- ✅ E2E tests: All passing on staging
- ✅ Accessibility tests: No WCAG AA violations

### Performance
- ✅ Lighthouse CI: Performance >90, Accessibility >95, Best Practices >90
- ✅ First Contentful Paint <1.5s
- ✅ Time to Interactive <3s

### Security
- ✅ npm audit: No critical vulnerabilities
- ✅ CSP headers: Configured
- ✅ File upload validation: Implemented
- ✅ Input sanitization: Implemented

### Deployment
- ✅ Preview deployment: Working
- ✅ Production deployment: Successful
- ✅ Backend integration: Verified
- ✅ Application Insights: Logging correctly

---

## Common Issues & Solutions

### Issue: OpenAPI client generation fails
**Solution:** Ensure backend is running and OpenAPI spec is valid. Download spec manually and inspect for errors.

### Issue: CORS errors in development
**Solution:** Ensure backend CORS middleware allows `http://localhost:5173` (Vite default port).

### Issue: LocalStorage quota exceeded
**Solution:** Implement auto-cleanup of old analyses (>7 days) or limit to 10 most recent.

### Issue: File upload fails silently
**Solution:** Check file validation logic, ensure FileReader API is used correctly, check network tab for errors.

### Issue: Analysis hangs (no response after 30s)
**Solution:** Check backend logs, increase timeout to 60s (backend can take 20-30s), add cancel mechanism.

### Issue: Application Insights not logging
**Solution:** Verify instrumentation key, check initialization code, test with `appInsights.trackEvent()` manually.

---

**Status Tracking:**
- Use this checklist to track progress during Phase 2 implementation
- Update checkboxes as tasks are completed
- Raise blockers immediately to Developer Lead

**Questions?** Contact Developer Lead or refer to [Frontend FRD v1.1](../specs/features/frontend-ag-ui.md)
