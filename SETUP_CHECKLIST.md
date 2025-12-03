# 🚀 Setup Checklist - AutoML Platform

Complete this checklist to get your AutoML platform up and running.

---

## ✅ Prerequisites

### Required Software
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Git installed
- [ ] Docker installed (optional, for containerized deployment)
- [ ] Ollama installed (optional, for local LLM)

### Verify Installation
```bash
python --version    # Should be 3.10+
node --version      # Should be 18+
npm --version       # Should be 9+
docker --version    # Should be 20+
```

---

## 📦 Backend Setup

### 1. Clone Repository
- [ ] Clone the repository
```bash
git clone <repository-url>
cd automl-agent
```

### 2. Create Virtual Environment
- [ ] Create Python virtual environment
```bash
python -m venv venv
```

- [ ] Activate virtual environment
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install Dependencies
- [ ] Install Python packages
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment
- [ ] Copy environment file
```bash
cp .env.example .env
```

- [ ] Edit `.env` with your settings
```bash
# Required
LLM_MODE=ollama

# Optional (for data sources)
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
HF_TOKEN=your_token
```

### 5. Create Directories
- [ ] Create necessary directories
```bash
mkdir -p artifacts data
```

### 6. Test Backend
- [ ] Start backend server
```bash
uvicorn app.main:app --reload
```

- [ ] Verify backend is running
```bash
curl http://localhost:8000/health
```

- [ ] Check API docs
```
Open: http://localhost:8000/docs
```

---

## 🎨 Frontend Setup

### 1. Navigate to Frontend
- [ ] Change to frontend directory
```bash
cd frontend
```

### 2. Install Dependencies
- [ ] Install Node packages
```bash
npm install
```

### 3. Configure Environment
- [ ] Copy environment file
```bash
cp .env.example .env
```

### 4. Test Frontend
- [ ] Start development server
```bash
npm run dev
```

- [ ] Verify frontend is running
```
Open: http://localhost:3000
```

### 5. Build for Production (Optional)
- [ ] Build frontend
```bash
npm run build
```

---

## 🐳 Docker Setup (Alternative)

### 1. Build Docker Image
- [ ] Build the image
```bash
docker build -t automl-platform .
```

### 2. Start with Docker Compose
- [ ] Start all services
```bash
docker-compose up -d
```

### 3. Verify Services
- [ ] Check running containers
```bash
docker-compose ps
```

- [ ] View logs
```bash
docker-compose logs -f
```

### 4. Access Application
- [ ] Open application
```
http://localhost:8000
```

---

## 🤖 LLM Setup

### Option 1: Ollama (Local - Recommended)

- [ ] Install Ollama
```bash
# Visit: https://ollama.ai/download
```

- [ ] Pull a model
```bash
ollama pull mistral
```

- [ ] Verify Ollama is running
```bash
curl http://localhost:11434/api/generate
```

- [ ] Update `.env`
```bash
LLM_MODE=ollama
OLLAMA_MODEL=mistral:latest
```

### Option 2: OpenAI

- [ ] Get API key from https://platform.openai.com/
- [ ] Update `.env`
```bash
LLM_MODE=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

### Option 3: Anthropic Claude

- [ ] Get API key from https://console.anthropic.com/
- [ ] Update `.env`
```bash
LLM_MODE=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

---

## 📊 Data Sources Setup (Optional)

### Kaggle

- [ ] Create Kaggle account
- [ ] Get API credentials from https://www.kaggle.com/settings
- [ ] Update `.env`
```bash
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### HuggingFace

- [ ] Create HuggingFace account
- [ ] Get token from https://huggingface.co/settings/tokens
- [ ] Update `.env`
```bash
HF_TOKEN=hf_...
```

---

## 🧪 Testing

### Backend Tests
- [ ] Run backend tests
```bash
pytest
```

- [ ] Check coverage
```bash
pytest --cov=app --cov-report=html
```

### Frontend Tests
- [ ] Run frontend tests
```bash
cd frontend
npm test
```

### Integration Test
- [ ] Run full system test
```bash
python test_system.py
```

---

## 🚀 First Run

### 1. Start Services

**Option A: Separate Servers**
- [ ] Terminal 1: Start backend
```bash
uvicorn app.main:app --reload
```

- [ ] Terminal 2: Start frontend
```bash
cd frontend && npm run dev
```

**Option B: Docker**
- [ ] Start with Docker Compose
```bash
docker-compose up
```

### 2. Access Application
- [ ] Open browser to http://localhost:3000 (dev) or http://localhost:8000 (docker)

### 3. Test ML Pipeline
- [ ] Click "Start New Run"
- [ ] Enter problem statement: "Predict customer churn"
- [ ] Click "Start Run"
- [ ] Watch progress in real-time
- [ ] Verify completion

---

## 🔧 CI/CD Setup (Optional)

### GitHub Actions

- [ ] Push code to GitHub
```bash
git remote add origin <your-repo-url>
git push -u origin main
```

- [ ] Add GitHub Secrets
```
Settings → Secrets → Actions → New repository secret
```

Required secrets:
- [ ] `DOCKER_USERNAME`
- [ ] `DOCKER_PASSWORD`
- [ ] `RENDER_API_KEY` (if using Render)
- [ ] `RENDER_SERVICE_ID` (if using Render)

- [ ] Verify workflow runs
```
Actions tab in GitHub
```

---

## ☁️ Cloud Deployment (Optional)

### Render

- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create new Web Service
- [ ] Select Dockerfile
- [ ] Add environment variables
- [ ] Deploy

### Railway

- [ ] Install Railway CLI
```bash
npm install -g @railway/cli
```

- [ ] Login and deploy
```bash
railway login
railway up
```

### Docker Hub

- [ ] Create Docker Hub account
- [ ] Login
```bash
docker login
```

- [ ] Push image
```bash
docker tag automl-platform your-username/automl-platform
docker push your-username/automl-platform
```

---

## ✅ Verification Checklist

### Backend
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Can start a run via API
- [ ] Logs are being written to `artifacts/`

### Frontend
- [ ] Home page loads
- [ ] Can navigate between pages
- [ ] Can submit new run form
- [ ] Real-time status updates work
- [ ] Can view past runs

### Integration
- [ ] Frontend can communicate with backend
- [ ] File upload works
- [ ] Status polling works
- [ ] Artifacts can be downloaded

### LLM
- [ ] LLM responds to prompts
- [ ] Problem statement parsing works
- [ ] Model selection works

### Data
- [ ] Can search Kaggle (if configured)
- [ ] Can search HuggingFace (if configured)
- [ ] Synthetic data generation works

---

## 🎉 Success Criteria

You're ready to go when:

- ✅ Backend starts without errors
- ✅ Frontend loads in browser
- ✅ Can complete a full ML pipeline run
- ✅ Results are displayed correctly
- ✅ Artifacts are generated
- ✅ Logs show progress

---

## 📚 Next Steps

After setup is complete:

1. **Read Documentation**
   - [ ] Review README.md
   - [ ] Read DEPLOYMENT.md
   - [ ] Check FRONTEND_BACKEND_INTEGRATION.md

2. **Try Examples**
   - [ ] Run example problem statements
   - [ ] Upload a CSV file
   - [ ] Try different ML tasks

3. **Customize**
   - [ ] Adjust training budgets
   - [ ] Configure preferred metrics
   - [ ] Add custom data sources

4. **Deploy**
   - [ ] Choose deployment platform
   - [ ] Configure production environment
   - [ ] Set up monitoring

---

## 🆘 Troubleshooting

### Backend won't start
- Check Python version (3.10+)
- Verify all dependencies installed
- Check `.env` file exists
- Look for port conflicts (8000)

### Frontend won't start
- Check Node version (18+)
- Run `npm install` again
- Clear `node_modules` and reinstall
- Check port 3000 is available

### LLM not responding
- Verify Ollama is running
- Check API keys are correct
- Test LLM endpoint directly
- Check network connectivity

### Docker issues
- Ensure Docker is running
- Check Docker Compose version
- Review container logs
- Verify port mappings

---

## 📞 Getting Help

If you encounter issues:

1. Check the troubleshooting section
2. Review error logs in `artifacts/`
3. Check GitHub Issues
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Logs

---

## ✨ You're All Set!

Once all checkboxes are complete, your AutoML platform is ready to use!

**Happy ML building! 🚀**
