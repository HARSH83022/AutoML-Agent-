# Deployment Guide - AutoML Platform

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [CI/CD Pipeline](#cicd-pipeline)
4. [Cloud Deployment](#cloud-deployment)
5. [Environment Variables](#environment-variables)

---

## Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama (for local LLM)

### Backend Setup
```bash
# Navigate to project root
cd automl-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start backend
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`
Backend API at `http://localhost:8000`

---

## Docker Deployment

### Quick Start with Docker Compose
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production with Nginx
```bash
# Start with production profile
docker-compose --profile production up -d
```

### Individual Docker Build
```bash
# Build image
docker build -t automl-platform .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/artifacts:/app/artifacts \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  --name automl \
  automl-platform
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes a complete CI/CD pipeline that:

1. **Runs on every push/PR** to `main` or `develop`
2. **Backend Tests**: Runs pytest with coverage
3. **Frontend Tests**: Linting, testing, and build
4. **Docker Build**: Builds and pushes to Docker Hub
5. **Auto-Deploy**: Deploys to production on main branch

### Required GitHub Secrets

Add these in **Settings → Secrets → Actions**:

```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
RENDER_API_KEY=your_render_api_key
RENDER_SERVICE_ID=your_render_service_id
SLACK_WEBHOOK=your_slack_webhook_url (optional)
```

### Workflow Triggers

```yaml
# Automatic on push
git push origin main

# Manual trigger
gh workflow run ci-cd.yml
```

---

## Cloud Deployment

### Option 1: Render

1. **Create New Web Service**
   - Connect GitHub repository
   - Select `Dockerfile` as build method
   - Set environment variables

2. **Configure**
   ```
   Build Command: docker build -t automl .
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables**
   - Add all variables from `.env`
   - Set `PORT=8000`

### Option 2: Railway

1. **Deploy from GitHub**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login
   railway login

   # Deploy
   railway up
   ```

2. **Configure**
   - Add environment variables in dashboard
   - Set custom domain (optional)

### Option 3: AWS ECS

1. **Push to ECR**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push
   docker tag automl-platform:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/automl:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/automl:latest
   ```

2. **Create ECS Service**
   - Use Fargate launch type
   - Configure task definition with image
   - Set up load balancer
   - Configure auto-scaling

### Option 4: Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/automl
gcloud run deploy automl \
  --image gcr.io/PROJECT-ID/automl \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Environment Variables

### Required Variables

```bash
# LLM Configuration
LLM_MODE=ollama                    # ollama, openai, anthropic, gemini
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=mistral:latest

# Data Sources (Optional)
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
HF_TOKEN=your_huggingface_token

# Cloud LLM (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

### Optional Variables

```bash
# Paths
DATA_DIR=data
ARTIFACT_DIR=artifacts

# Synthetic Data
SYNTHETIC_DEFAULT_ROWS=2000

# Server
PORT=8000
HOST=0.0.0.0
```

---

## Monitoring & Logging

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Docker health
docker ps --filter "health=healthy"
```

### Logs

```bash
# Docker logs
docker-compose logs -f automl-platform

# Application logs
tail -f artifacts/*_system_log.txt
```

### Metrics

Access metrics at:
- `/metrics` - Prometheus metrics
- `/health` - Health status
- `/status/{run_id}` - Run-specific status

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  automl-platform:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### Load Balancing

Use Nginx or cloud load balancer:

```nginx
upstream automl_backend {
    server automl-1:8000;
    server automl-2:8000;
    server automl-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://automl_backend;
    }
}
```

---

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find and kill process
   lsof -ti:8000 | xargs kill -9
   ```

2. **Docker build fails**
   ```bash
   # Clear cache and rebuild
   docker-compose build --no-cache
   ```

3. **Frontend can't connect to backend**
   - Check VITE_API_URL in frontend/.env
   - Verify CORS settings in backend

4. **Ollama not responding**
   ```bash
   # Restart Ollama
   docker-compose restart ollama
   ```

---

## Security

### Production Checklist

- [ ] Change default secrets
- [ ] Enable HTTPS (use Let's Encrypt)
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS properly
- [ ] Use environment-specific configs
- [ ] Enable authentication (if needed)
- [ ] Regular security updates

### SSL/TLS Setup

```bash
# Using Certbot
certbot --nginx -d yourdomain.com
```

---

## Backup & Recovery

### Database Backup

```bash
# Backup SQLite database
cp runs.db runs.db.backup

# Automated backup
0 2 * * * cp /app/runs.db /backups/runs_$(date +\%Y\%m\%d).db
```

### Artifact Backup

```bash
# Sync to S3
aws s3 sync ./artifacts s3://your-bucket/artifacts/
```

---

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [repository-url]/docs
- Email: support@yourcompany.com
