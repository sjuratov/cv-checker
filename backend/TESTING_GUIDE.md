# Testing Phase 3 - AI Agent Implementation

## Prerequisites

1. **Azure OpenAI Setup**
   - Deploy gpt-4.1 (or gpt-4) model in Azure OpenAI
   - Note your endpoint URL and deployment name
   - Assign "Cognitive Services OpenAI User" role to your identity

2. **Authentication Setup**
   Choose one of these methods:

   **Option A: Azure CLI (Recommended for local dev)**
   ```bash
   az login
   ```

   **Option B: Service Principal**
   Create `.env` file with:
   ```bash
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4-1
   AZURE_TENANT_ID=your-tenant-id
   AZURE_CLIENT_ID=your-client-id
   AZURE_CLIENT_SECRET=your-client-secret
   ```

## Quick Start

### 1. Start the Server

```bash
cd /Users/sjuratovic/repos/cv-checker/backend
uv run uvicorn app.main:app --reload
```

### 2. Test Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "cv-checker-api",
  "azure_openai": "connected"
}
```

### 3. Test CV Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "cv_markdown": "# John Doe\n\n## Professional Summary\nSenior Software Engineer with 5+ years of experience in Python development.\n\n## Skills\n- Python, FastAPI, Django\n- Azure, Docker, Kubernetes\n- SQL, MongoDB, Redis\n\n## Experience\n### Senior Developer at TechCorp (2020-2024)\n- Built REST APIs using FastAPI\n- Deployed microservices to Azure\n- Led team of 3 developers",
    "job_description": "Looking for a Senior Python Developer with FastAPI experience and Azure cloud knowledge. Must have 3+ years of experience building REST APIs and working with containerized applications."
  }'
```

## Expected Workflow Execution

When you submit an analysis request, you should see logs like:

```
============================================================
Starting CV Checker workflow execution
============================================================
Step 1/4: Parsing job description...
✓ Job parsed - Title: Senior Python Developer
Step 2/4: Parsing CV...
✓ CV parsed - Candidate: John Doe, Experience: 5 years
Step 3/4: Analyzing compatibility...
Deterministic score: 88.50 (skills: 90.00%, experience: 85.00%)
LLM validation complete - Total: 82.00
✓ Analysis complete - Score: 86.10/100 (B+)
Step 4/4: Generating recommendations...
✓ Report generated - 7 recommendations
============================================================
Workflow complete - Final Score: 86.10/100
============================================================
```

## Troubleshooting

### Azure OpenAI Connection Issues

**Error:** `Failed to create Azure OpenAI client`

**Solutions:**
1. Verify endpoint URL is correct
2. Check deployment name matches your model
3. Ensure you're authenticated:
   ```bash
   az account show
   ```
4. Verify RBAC role assignment:
   ```bash
   az role assignment list --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{resource}
   ```

### JSON Parsing Errors

**Error:** `Invalid JSON response from agent`

**Cause:** LLM didn't return valid JSON

**Solutions:**
- Check LLM temperature (should be 0.3)
- Verify model supports JSON mode
- Review agent system prompts
- Check LLM response in logs

### Low Scores

**Issue:** All candidates get low scores

**Check:**
- Skill normalization (case-insensitive matching)
- LLM semantic analysis reasoning
- Deterministic vs LLM breakdown in logs

### Timeout

**Error:** Request times out

**Solutions:**
- Increase timeout in `app/utils/azure_openai.py`
- Check Azure OpenAI quota/rate limits
- Simplify CV/job description for testing

## Monitoring

### Key Metrics to Watch

1. **Latency**
   - Target: <30 seconds per analysis
   - Current: Check logs for "elapsed" time

2. **Score Distribution**
   - Expect variety: 60-95 range
   - If all scores similar, check hybrid scoring

3. **Agent Success Rate**
   - Each step should complete
   - Monitor for JSON parsing failures

4. **Azure OpenAI Costs**
   - GPT-4.1: ~$0.01-0.02 per analysis
   - Monitor token usage in Azure Portal

## Sample Test Cases

### Test Case 1: Perfect Match
```json
{
  "cv_markdown": "# Jane Smith\n## Senior Python Engineer\n7 years Python, FastAPI expert, Azure certified\n\n## Experience\n- Built microservices with FastAPI\n- Deployed to Azure Kubernetes Service\n- 5 years REST API development",
  "job_description": "Senior Python Developer, FastAPI required, 5+ years experience, Azure knowledge essential"
}
```
**Expected Score:** 90-100 (A range)

### Test Case 2: Skill Gaps
```json
{
  "cv_markdown": "# Bob Johnson\n## Java Developer\n3 years Java/Spring Boot\n\n## Experience\n- Built enterprise applications\n- MySQL databases",
  "job_description": "Senior Python Developer, FastAPI required, 5+ years, Azure/Kubernetes essential"
}
```
**Expected Score:** 30-50 (D-F range)

### Test Case 3: Transferable Skills
```json
{
  "cv_markdown": "# Alice Wong\n## Backend Engineer\n6 years experience\n- Python, Django, Flask\n- AWS Lambda, CloudFormation\n- Docker, ECS\n- PostgreSQL, DynamoDB",
  "job_description": "Senior Python Developer, FastAPI experience, Azure cloud, 5+ years, containerization"
}
```
**Expected Score:** 70-85 (B-C range)
- Should identify AWS→Azure transferability
- Should recognize Django/Flask→FastAPI similarity

## Validation

### Verify Hybrid Scoring

Check response breakdown:
```json
{
  "breakdown": {
    "deterministic": {
      "weight": "60%",
      "score": 85.0,
      "skill_match": 90.0,
      "experience_alignment": 75.0
    },
    "llm_semantic": {
      "weight": "40%",
      "score": 80.0,
      "semantic_match": 82.0,
      "soft_skills": 76.0
    }
  }
}
```

**Verify:**
- Final score = (85 × 0.6) + (80 × 0.4) = 83
- Skill match > experience (weighted 40% vs 20% in det.)
- Semantic > soft skills (weighted 25% vs 15% in LLM)

### Verify Recommendations

Should include:
- Priority levels (HIGH, MEDIUM, LOW)
- Categories (ADD_SKILL, MODIFY_CONTENT, etc.)
- Specific actions
- Rationale

Example:
```
[HIGH] Add Kubernetes certification (CKA) - Critical skill gap for DevOps role
[MEDIUM] Emphasize FastAPI projects in summary - You have experience but it's buried
[LOW] Consider GraphQL learning - Nice-to-have for future projects
```

## Performance Benchmarks

| Metric | Target | Notes |
|--------|--------|-------|
| Total latency | <30s | Full workflow |
| JobParser | <3s | Single LLM call |
| CVParser | <3s | Single LLM call |
| Analyzer (Det) | <1s | Pure computation |
| Analyzer (LLM) | <5s | Semantic validation |
| ReportGenerator | <5s | Recommendation generation |
| Overhead | <3s | Orchestration, model conversion |

## Next Steps After Testing

1. **Collect Sample Data**
   - 10+ diverse job descriptions
   - 20+ CV samples (various experience levels)
   - Expected score ranges

2. **Write Unit Tests**
   - Mock OpenAI client
   - Test deterministic scorer independently
   - Validate JSON parsing

3. **Write Integration Tests**
   - End-to-end workflow
   - Error scenarios
   - Edge cases (empty CVs, huge CVs)

4. **Optimize**
   - Profile slow steps
   - Tune prompts for tokens
   - Consider prompt caching
   - Add retry logic

5. **Document**
   - API usage guide
   - Troubleshooting playbook
   - Deployment guide
