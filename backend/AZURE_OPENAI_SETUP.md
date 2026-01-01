# Azure OpenAI Configuration Guide

## The Error You're Seeing

```
Token tenant fcbfc09a-8ad2-4370-929e-1946f1aa1f6f does not match resource tenant
```

This means the Azure AD tenant used for authentication doesn't match the tenant where your Azure OpenAI resource is deployed.

## Quick Fix: Use API Key Authentication

### Step 1: Get Your Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Click on "Keys and Endpoint" in the left menu
4. Copy:
   - **Endpoint** (e.g., `https://your-resource.openai.azure.com/`)
   - **Key 1** or **Key 2**
   - **Deployment name** (e.g., `gpt-4`, `gpt-35-turbo`)

### Step 2: Update Your `.env` File

Edit `/Users/sjuratovic/repos/cv-checker/backend/.env`:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://YOUR-ACTUAL-RESOURCE.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=YOUR-DEPLOYMENT-NAME
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_API_KEY=YOUR-API-KEY-HERE
```

**Replace:**
- `YOUR-ACTUAL-RESOURCE` - with your actual Azure OpenAI resource name
- `YOUR-DEPLOYMENT-NAME` - with your deployment name (e.g., `gpt-4-1`, `gpt-35-turbo`)
- `YOUR-API-KEY-HERE` - with the key you copied from Azure Portal

### Step 3: Restart Your Backend

Stop the backend server (Ctrl+C) and restart it:

```bash
cd /Users/sjuratovic/repos/cv-checker/backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

## Alternative: Use Entra ID (Azure AD) Authentication

If you prefer to use Entra ID authentication without API keys:

### Option A: Use Azure CLI Login (Match Tenant)

1. Login to Azure CLI with the correct tenant:
   ```bash
   az login --tenant YOUR-AZURE-OPENAI-RESOURCE-TENANT-ID
   ```

2. Remove or comment out `AZURE_OPENAI_API_KEY` from `.env`

3. Make sure your Azure OpenAI endpoint is correct in `.env`

### Option B: Use Service Principal

1. Create a service principal in the same tenant as your Azure OpenAI resource
2. Grant it "Cognitive Services OpenAI User" role on your Azure OpenAI resource
3. Configure in `.env`:
   ```bash
   AZURE_TENANT_ID=your-azure-openai-resource-tenant-id
   AZURE_CLIENT_ID=your-service-principal-client-id
   AZURE_CLIENT_SECRET=your-service-principal-client-secret
   ```

## Verification

After configuration, test with:

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_text": "Test CV",
    "job_description": "Test Job"
  }'
```

You should not see tenant mismatch errors anymore.

## Troubleshooting

### "404 Resource Not Found"
- Check that `AZURE_OPENAI_ENDPOINT` is correct
- Verify the deployment name matches what's in your Azure OpenAI resource

### "401 Unauthorized"
- Verify your API key is correct
- For Entra ID: ensure you have the "Cognitive Services OpenAI User" role

### "Deployment not found"
- Check that `AZURE_OPENAI_DEPLOYMENT` matches the exact deployment name in Azure Portal
