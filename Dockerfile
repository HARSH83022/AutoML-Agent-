# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./

RUN npm install && npm install -g vite

COPY frontend/ ./

RUN chmod -R 755 /app/frontend/node_modules

RUN npm run build


# Stage 2: Python Backend
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY app/ ./app/
COPY .env.example ./.env

# Copy built frontend output to backend static folder
COPY --from=frontend-builder /app/frontend/dist ./app/static

# Create necessary directories
RUN mkdir -p artifacts data

# Expose FastAPI port
EXPOSE 8000

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
# Use shell form to properly expand $PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

