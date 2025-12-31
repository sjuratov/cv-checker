# CV Checker Backend

AI-powered CV analysis and job matching system built with FastAPI and Microsoft Agent Framework.

## Features

- 🤖 Multi-agent AI workflow using Microsoft Agent Framework
- 🔒 Secure Azure OpenAI integration with Entra ID authentication
- 📊 Hybrid scoring algorithm (60% deterministic + 40% LLM semantic)
- ⚡ FastAPI with async support and automatic OpenAPI documentation
- 🎯 Type-safe with Pydantic models
- 🧪 Comprehensive testing suite

## Architecture

The system uses a sequential agent orchestration pattern with four specialized agents:
1. **JobParser Agent**: Extracts requirements from job descriptions
2. **CVParser Agent**: Extracts candidate information from CVs
3. **Analyzer Agent**: Performs hybrid scoring (deterministic + LLM)
4. **ReportGenerator Agent**: Creates actionable recommendations

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Azure OpenAI access with GPT-4.1 deployment
- Azure CLI (for local development) or service principal credentials

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cv-checker/backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

5. Authenticate with Azure (if using Azure CLI method):
```bash
az login
```

### Running the Application

**Development Mode:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Usage

### Analyze CV Endpoint

**POST /api/v1/analyze**

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_markdown": "# John Doe\n\n## Skills\n- Python (5 years)\n- FastAPI\n- Azure",
    "job_description": "Senior Python Developer needed with 3+ years FastAPI experience."
  }'
```

**Response:**
```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "overall_score": 87.5,
  "skill_matches": [...],
  "experience_match": {...},
  "education_match": {...},
  "strengths": ["Strong Python experience"],
  "gaps": ["Limited cloud deployment experience"],
  "recommendations": ["Highlight Azure projects"]
}
```

### Health Check

**GET /api/v1/health**

```bash
curl http://localhost:8000/api/v1/health
```

## Testing

Run the test suite:
```bash
pytest
```

With coverage report:
```bash
pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── agents/                 # AI agent implementations
│   ├── models/                 # Pydantic models
│   ├── services/               # Business logic
│   ├── repositories/           # Data access layer
│   └── utils/                  # Utility functions
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Development

### Code Quality

Format code:
```bash
black app/ tests/
```

Lint code:
```bash
ruff check app/ tests/
```

Type checking:
```bash
mypy app/
```

### Environment Variables

Required variables (see `.env.example`):
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT`: GPT-4.1 deployment name
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-08-01-preview)

Optional for service principal auth:
- `AZURE_TENANT_ID`: Azure AD tenant ID
- `AZURE_CLIENT_ID`: Service principal client ID
- `AZURE_CLIENT_SECRET`: Service principal secret

## Azure Setup

### 1. Create Azure OpenAI Resource

```bash
az cognitiveservices account create \
  --name cv-checker-openai \
  --resource-group cv-checker-rg \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

### 2. Deploy GPT-4.1 Model

```bash
az cognitiveservices account deployment create \
  --name cv-checker-openai \
  --resource-group cv-checker-rg \
  --deployment-name gpt-4-1 \
  --model-name gpt-4 \
  --model-version "1106-Preview" \
  --model-format OpenAI \
  --sku-name "Standard" \
  --sku-capacity 1
```

### 3. Assign RBAC Role

For your user (local development):
```bash
az role assignment create \
  --role "Cognitive Services OpenAI User" \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --scope /subscriptions/<subscription-id>/resourceGroups/cv-checker-rg/providers/Microsoft.CognitiveServices/accounts/cv-checker-openai
```

For managed identity (production):
```bash
az role assignment create \
  --role "Cognitive Services OpenAI User" \
  --assignee <managed-identity-id> \
  --scope /subscriptions/<subscription-id>/resourceGroups/cv-checker-rg/providers/Microsoft.CognitiveServices/accounts/cv-checker-openai
```

## Troubleshooting

### Authentication Errors

If you see "DefaultAzureCredential failed to retrieve a token":
1. Ensure you're logged in: `az login`
2. Verify RBAC role assignment
3. Check endpoint URL is correct
4. For service principal, verify all three variables (tenant, client ID, secret)

### Import Errors

If you see module import errors:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify Python version: `python --version` (should be 3.11+)

## Architecture Decisions

This implementation follows these ADRs:
- **ADR-001**: Microsoft Agent Framework Sequential Orchestration
- **ADR-002**: Azure OpenAI Integration with Entra ID
- **ADR-003**: Hybrid Scoring Algorithm (60% deterministic + 40% LLM)
- **ADR-004**: No Database V1 (in-memory processing, Cosmos DB ready)
- **ADR-005**: FastAPI Backend Architecture

## License

See LICENSE file in the project root.

## Support

For issues and questions, please refer to the project documentation in `/docs`.
