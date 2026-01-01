#!/bin/bash

echo "========================================================================"
echo "End-to-End Test for Both Fixes"
echo "========================================================================"
echo ""
echo "This script will:"
echo "1. Check if the backend is running"
echo "2. Submit a test analysis"
echo "3. Check CosmosDB for duplicate records"
echo "4. Provide frontend testing instructions"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo "Checking if backend is running on http://localhost:8000..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is NOT running${NC}"
    echo ""
    echo "Please start the backend first:"
    echo "  cd backend"
    echo "  uv run uvicorn app.main:app --reload"
    echo ""
    exit 1
fi

echo ""
echo "========================================================================"
echo "Submitting test analysis..."
echo "========================================================================"

# Create a simple CV and job description for testing
CV_TEXT="# John Doe
Software Engineer

## Skills
- Python (5 years)
- React (3 years)
- Azure (2 years)

## Experience
Senior Software Engineer at Tech Co (2020-2025)"

JOB_TEXT="We are looking for a Senior Software Engineer with:
- 5+ years Python experience
- React experience
- Cloud experience (Azure preferred)
- Strong communication skills"

# Submit analysis request
echo "Sending analysis request..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d "{
    \"cv_markdown\": \"$CV_TEXT\",
    \"job_description\": \"$JOB_TEXT\",
    \"cv_filename\": \"test_cv.pdf\"
  }")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Analysis submitted successfully${NC}"
    ANALYSIS_ID=$(echo "$RESPONSE" | grep -o '"analysis_id":"[^"]*"' | cut -d'"' -f4)
    echo "Analysis ID: $ANALYSIS_ID"
    echo ""
else
    echo -e "${RED}❌ Analysis submission failed${NC}"
    exit 1
fi

echo "========================================================================"
echo "Checking CosmosDB for duplicate records..."
echo "========================================================================"
cd "$(dirname "$0")/.."
cd backend
uv run python ../scripts/test_both_fixes.py

echo ""
echo "========================================================================"
echo "Frontend Testing Instructions (Fix #1 - Blank Page)"
echo "========================================================================"
echo ""
echo -e "${YELLOW}Please test manually:${NC}"
echo ""
echo "1. Open http://localhost:5173/ in your browser"
echo "2. Upload a CV and enter a job description"
echo "3. Click 'Analyze CV' and wait for results"
echo "4. Verify results display correctly"
echo "5. Click browser back button OR navigate to http://localhost:5173/"
echo ""
echo -e "${GREEN}✅ EXPECTED:${NC} Upload page shows with inputs"
echo -e "${RED}❌ OLD BUG:${NC} Blank page with no controls"
echo ""
echo "========================================================================"
