# # Multi-stage build for production

# # Stage 1: Build Frontend
# FROM node:18-alpine AS frontend-builder

# WORKDIR /app/frontend

# # Copy package files and install dependencies
# COPY frontend/package*.json ./
# RUN npm install && npm install -g vite

# # Copy frontend source
# COPY frontend/ ./

# # Fix permission issue for vite binary
# RUN chmod -R 755 /app/frontend/node_modules

# # Build Vite frontend
# RUN npm run build

# # Stage 2: Python Backend
# FROM python:3.10-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Copy backend requirements and install dependencies
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend code
# COPY app/ ./app/
# COPY .env.example ./.env

# # Copy built frontend into FastAPI static directory
# COPY --from=frontend-builder /app/frontend/dist ./app/static

# # Create needed directories
# RUN mkdir -p artifacts data

# # Expose port (not required by Railway but safe)
# EXPOSE 8000

# # Health check (optional)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# # === IMPORTANT: Run server using Railway's dynamic PORT ===
# CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT

#!/bin/sh

echo "Starting FastAPI with PORT=${PORT}"

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
