# LinkedIn URL Fetching - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (optional, for containerized deployment)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Environment Variables

Create `.env` file in `backend/` directory:

```bash
# Azure OpenAI (required for CV analysis)
AZURE_OPENAI_ENDPOINT=https://your-openai-instance.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# LinkedIn Scraper Settings (optional - defaults shown)
LINKEDIN_SCRAPER_TIMEOUT=15000  # 15 seconds
RATE_LIMIT_PER_MINUTE=5
RATE_LIMIT_PER_HOUR=20

# CORS Settings (for local frontend)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Run Backend Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python -m app.main
```

Backend API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/api/v1/docs`

### 4. Test Backend

```bash
# Run unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run all tests with coverage
pytest --cov=app tests/ -v
```

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend

npm install
```

### 2. Environment Variables

Create `.env` file in `frontend/` directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Frontend Dev Server

```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 4. Build for Production

```bash
npm run build

# Preview production build
npm run preview
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
cd backend

docker build -t cv-checker-backend:linkedin .
```

### 2. Run Docker Container

```bash
docker run -d \
  -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT=your-endpoint \
  -e AZURE_OPENAI_API_KEY=your-key \
  -e AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o \
  --name cv-checker-api \
  cv-checker-backend:linkedin
```

### 3. Check Container Logs

```bash
docker logs cv-checker-api -f
```

### 4. Stop Container

```bash
docker stop cv-checker-api
docker rm cv-checker-api
```

---

## Testing LinkedIn URL Fetching

### Manual Testing via API

```bash
# Test manual job submission
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "manual",
    "content": "We are seeking a Senior Python Developer with 5+ years of experience..."
  }'

# Test LinkedIn URL fetching
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "linkedin_url",
    "url": "https://www.linkedin.com/jobs/view/123456789/"
  }'
```

### Frontend Testing

1. Open `http://localhost:5173`
2. Upload a CV (sample in `frontend/public/sample-cv.md`)
3. Click "LinkedIn URL" toggle
4. Paste a LinkedIn job URL
5. Click "Fetch Job Description"
6. Verify job description populates
7. Click "Analyze Match" to run full analysis

### Test URLs

**Valid LinkedIn URLs:**
- `https://www.linkedin.com/jobs/view/3780715035/`
- `https://linkedin.com/jobs/view/3780715035/`
- `https://www.linkedin.com/jobs/view/3780715035/?refId=abc123`

**Invalid URLs (should show error):**
- `https://google.com/jobs/123` (wrong domain)
- `https://www.linkedin.com/in/profile/` (profile page)
- `not-a-url` (invalid format)

---

## Troubleshooting

### Backend Issues

**Problem:** `playwright.errors.Error: Executable doesn't exist`

**Solution:**
```bash
playwright install chromium
```

**Problem:** `ModuleNotFoundError: No module named 'slowapi'`

**Solution:**
```bash
pip install -r requirements.txt
```

**Problem:** Rate limit errors during testing

**Solution:**
- Wait 1 minute between requests
- Or disable rate limiting in development (comment out `@limiter.limit` decorator)

### Frontend Issues

**Problem:** `Failed to fetch` error when clicking "Fetch Job Description"

**Solution:**
- Verify backend is running: `curl http://localhost:8000/api/v1/health`
- Check `VITE_API_BASE_URL` in `.env`
- Check CORS settings in backend `.env`

**Problem:** Toggle buttons not styled correctly

**Solution:**
- Restart Vite dev server: `npm run dev`
- Clear browser cache
- Verify `App.css` includes LinkedIn URL styles

### Docker Issues

**Problem:** Docker build fails at Playwright install

**Solution:**
- Ensure Docker has enough memory (at least 4GB)
- Check Dockerfile has all Playwright system dependencies

**Problem:** Container runs but scraping fails

**Solution:**
- Check container logs: `docker logs cv-checker-api`
- Verify headless mode supported: `docker exec cv-checker-api playwright --version`

---

## Performance Optimization

### Backend

1. **Browser Instance Pooling:**
   - Current implementation creates one browser instance at startup
   - For high load, implement browser pool with max 5-10 instances

2. **Caching:**
   - Cache scraped jobs for 1 hour to reduce redundant requests
   - Use Redis or in-memory cache

3. **Rate Limiting:**
   - Default: 5/min, 20/hour per IP
   - Adjust based on production metrics

### Frontend

1. **Lazy Loading:**
   - Components already code-split via Vite
   - No additional optimization needed for Phase 2

2. **API Response Caching:**
   - Use React Query for automatic caching (future enhancement)

---

## Monitoring

### Key Metrics to Track

**Backend (Application Insights):**
- `linkedin_scrape_started` - Total scraping attempts
- `linkedin_scrape_completed` - Successful scrapes
- `linkedin_scrape_failed` - Failed scrapes (by error type)
- Success rate: `(completed / started) * 100`

**Frontend (Analytics):**
- `linkedin_url_fetch_initiated` - User clicks "Fetch"
- `linkedin_url_fetch_success` - Successful fetches
- `linkedin_url_fetch_failed` - Failed fetches (by error type)
- Mode preference: `linkedin_url` vs `manual`

### Alerts

Set up alerts for:
- Scraping success rate <85% for >1 hour
- Average scrape duration >20 seconds
- Anti-bot detection rate >5%

---

## Common Commands

### Backend

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest

# Run specific test file
pytest tests/unit/test_linkedin_validator.py -v

# Check code coverage
pytest --cov=app --cov-report=html

# Lint code
ruff check app/

# Format code
black app/
```

### Frontend

```bash
# Dev server
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Lint
npm run lint

# Type check
npm run type-check
```

### Docker

```bash
# Build
docker build -t cv-checker-backend .

# Run
docker run -p 8000:8000 cv-checker-backend

# Shell into container
docker exec -it cv-checker-api /bin/bash

# View logs
docker logs cv-checker-api -f
```

---

## Additional Resources

- **API Documentation:** http://localhost:8000/api/v1/docs (when running)
- **Playwright Docs:** https://playwright.dev/python/
- **SlowAPI Docs:** https://slowapi.readthedocs.io/
- **Zustand Docs:** https://zustand-demo.pmnd.rs/

---

## Support

For issues or questions:
1. Check logs: Backend (`uvicorn` output) and Frontend (browser console)
2. Review error messages (designed to be user-friendly)
3. Consult implementation plan: `/specs/plans/linkedin-url-fetching.md`
4. Check ADR: `/specs/adr/ADR-007-linkedin-job-scraping-playwright.md`

---

**Last Updated:** January 1, 2026
