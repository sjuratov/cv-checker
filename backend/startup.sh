#!/bin/bash

# CV Checker Backend Startup Script
# This script is used by Azure App Service

echo "Starting CV Checker API..."

# Run database migrations (future use)
# python -m alembic upgrade head

# Start the application with uvicorn
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}" \
    --workers "${WORKERS:-4}" \
    --log-level info \
    --access-log \
    --proxy-headers \
    --forwarded-allow-ips '*'
