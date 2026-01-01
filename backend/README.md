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
- **uv** - Fast Python package manager ([installation](https://github.com/astral-sh/uv))
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Or via pip
  pip install uv
  ```
- Azure OpenAI access with GPT-4.1 deployment
- Azure CLI (for local development) or service principal credentials
- **Docker Desktop** (for Cosmos DB emulator - Phase 2)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd cv-checker/backend
```

2. Create and activate virtual environment:
```bash
# Using uv (recommended - much faster)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or traditional method
# python -m venv venv
# source venv/bin/activate
```

3. Install dependencies:
```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or traditional pip
# pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.local .env
# Edit .env with your Azure OpenAI credentials
```

5. **[Phase 2] Start Cosmos DB Emulator:**
```bash
# Start the emulator (runs in Docker)
docker-compose up -d

# Wait for emulator to be ready (takes ~2 minutes first time)
docker-compose logs -f cosmosdb

# Initialize database and container (using uv)
uv run python scripts/init_cosmos.py
```

6. Authenticate with Azure (if using Azure CLI method):
```bash
az login
```

### Running the Application

**Development Mode:**
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production Mode:**
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Setup

Check that all services are running:
```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "service": "cv-checker-api",
#   "azure_openai": "connected",
#   "cosmos_db": "connected"
# }

# Check Cosmos DB emulator UI (local only)
open https://localhost:8081/_explorer/index.html
```

### Stopping Services

```bash
# Stop Cosmos DB emulator
docker-compose down

# Or keep data and just stop:
docker-compose stop
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

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "cv-checker-api",
  "azure_openai": "connected",
  "cosmos_db": "connected"
}
```

## Testing

Run the test suite:
```bash
uv run pytest
```

With coverage report:
```bash
uv run pytest --cov=app --cov-report=html
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
├── scripts/
│   └── init_cosmos.py          # Cosmos DB initialization
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── docker-compose.yml          # Cosmos DB emulator setup
├── .env.local                  # Local environment template
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Development

### Code Quality

Format code:
```bash
uv run black app/ tests/
```

Lint code:
```bash
uv run ruff check app/ tests/
```

Type checking:
```bash
uv run mypy app/
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

Cosmos DB (Phase 2):
- `COSMOS_CONNECTION_STRING`: Connection string (see `.env.local` for emulator default)
- `COSMOS_DATABASE_NAME`: Database name (default: cv-checker-db)
- `COSMOS_CONTAINER_NAME`: Container name (default: cv-checker-data)

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

### Cosmos DB Emulator Issues

**⚠️ KNOWN ISSUE: Emulator crashes on macOS (Exit Code 139)**

The Cosmos DB Linux emulator frequently crashes on macOS with segmentation faults. This is a known limitation.

**Recommended Solution: Use Azure Cosmos DB Free Tier instead**

```bash
# Create free Cosmos DB account (1000 RU/s free forever)
az cosmosdb create \
  --name cv-checker-cosmos-free \
  --resource-group cv-checker-rg \
  --kind GlobalDocumentDB \
  --locations regionName=eastus \
  --enable-free-tier true

# Get connection string
az cosmosdb keys list \
  --name cv-checker-cosmos-free \
  --resource-group cv-checker-rg \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv

# Update .env with Azure connection string
# COSMOS_CONNECTION_STRING=AccountEndpoint=https://cv-checker-cosmos-free.documents.azure.com:443/;AccountKey=...

# Initialize database
uv run python scripts/init_cosmos.py
```

**Alternative: Try the emulator (may not work on macOS)**
```bash
# Check if Docker is running
docker ps

# Check emulator logs
docker-compose logs cosmosdb

# Reset emulator (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
```

**Connection refused errors:**
```bash
# Verify emulator is healthy
docker-compose ps

# Should show STATUS as "healthy"
# If "unhealthy", wait 2-3 minutes for initialization

# Test emulator endpoint directly
curl -k https://localhost:8081/_explorer/index.html
```

**Port 8081 already in use:**
```bash
# Find what's using port 8081
lsof -i :8081

# Kill the process or change ports in docker-compose.yml
```

**macOS SSL certificate warnings:**
The emulator uses a self-signed certificate, which is expected. The Python SDK handles this automatically.

**"Evaluation version - 22 days left" message:**
This is normal for the emulator and resets automatically. The emulator is free for local development forever. However, for reliable local development on macOS, we recommend using Azure Cosmos DB free tier instead of the emulator.

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
3. Verify Python version: `python --version
- **ADR-008**: Cosmos DB Data Persistence (Phase 2)` (should be 3.11+)

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
