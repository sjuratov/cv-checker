# CV Checker Backend - Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- Azure OpenAI access (optional for Phase 1 & 2 testing)
- Azure CLI (for authentication)

## Installation (5 minutes)

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate on macOS/Linux:
source venv/bin/activate

# Activate on Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# For Phase 1 & 2, minimal config works:
# AZURE_OPENAI_ENDPOINT=https://placeholder.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT=gpt-4-1
```

## Running the Application

### Development Mode (Auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:

```bash
python app/main.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Verify Installation

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "cv-checker-api"
}
```

### 2. Test Analysis Endpoint (Mock Data)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_markdown": "# John Doe\n\n## Skills\n- Python (5 years)\n- FastAPI (2 years)\n- Azure\n\n## Experience\nSenior Developer at Tech Corp",
    "job_description": "We are seeking a Senior Python Developer with 3+ years of FastAPI experience and cloud platform knowledge."
  }'
```

Expected: JSON response with analysis_id, overall_score, skill_matches, etc.

### 3. Interactive API Documentation

Open in browser:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

You can test the API interactively from Swagger UI!

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=app --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/unit/test_models.py -v
```

### Run Integration Tests Only

```bash
pytest tests/integration/ -v
```

## Docker (Optional)

### Build Image

```bash
docker build -t cv-checker-backend .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT="https://placeholder.openai.azure.com/" \
  -e AZURE_OPENAI_DEPLOYMENT="gpt-4-1" \
  cv-checker-backend
```

## Common Commands

### Code Formatting

```bash
# Format code with Black
black app/ tests/

# Check formatting
black --check app/ tests/
```

### Linting

```bash
# Run Ruff linter
ruff check app/ tests/

# Auto-fix issues
ruff check --fix app/ tests/
```

### Type Checking

```bash
# Run MyPy
mypy app/
```

## Troubleshooting

### Import Errors

If you see "ModuleNotFoundError":
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify Python version: `python --version` (should be 3.11+)

### Port Already in Use

If port 8000 is busy:
```bash
# Use a different port
uvicorn app.main:app --reload --port 8080
```

### Tests Failing

Ensure you're in the backend directory and venv is activated:
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pytest -v
```

## Next Steps

### Phase 3: Implement AI Agents

1. Implement JobParser agent in `app/agents/job_parser.py`
2. Implement CVParser agent in `app/agents/cv_parser.py`
3. Implement Analyzer agent in `app/agents/analyzer.py`
4. Implement ReportGenerator agent in `app/agents/report_generator.py`
5. Implement Orchestrator in `app/agents/orchestrator.py`
6. Update `app/services/cv_checker.py` to use real agents

See `specs/plans/backend-implementation.md` for detailed Phase 3 tasks.

## Development Workflow

1. **Make changes** to code
2. **Run tests**: `pytest`
3. **Check formatting**: `black --check app/`
4. **Run linter**: `ruff check app/`
5. **Test manually**: Use Swagger UI at http://localhost:8000/api/v1/docs
6. **Commit changes**: `git add . && git commit -m "Description"`

## Useful URLs (when running)

- API Root: http://localhost:8000/
- Health Check: http://localhost:8000/api/v1/health
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

## Environment Variables Reference

### Required (Phase 3+)
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT` - GPT-4.1 deployment name

### Optional
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-08-01-preview)
- `AZURE_TENANT_ID` - For service principal auth
- `AZURE_CLIENT_ID` - For service principal auth
- `AZURE_CLIENT_SECRET` - For service principal auth
- `APP_ENV` - Environment (development/production)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING/ERROR)
- `CORS_ORIGINS` - Comma-separated allowed origins

## Support

For issues or questions:
1. Check `README.md` for detailed documentation
2. Review `IMPLEMENTATION_STATUS.md` for current status
3. See ADRs in `specs/adr/` for architecture decisions

---

**Ready to build!** 🚀

The foundation is complete. Start the server and test the API endpoints!
