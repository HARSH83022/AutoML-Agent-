#!/bin/bash
set -e

# Use PORT environment variable from Railway, default to 8000 if not set
PORT=${PORT:-8000}

echo "Starting application on port $PORT"

# Start uvicorn with the PORT variable
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
