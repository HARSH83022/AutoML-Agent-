# Render Deployment Guide for AutoML Agent

## 🚀 Quick Deployment Steps

### 1. Prerequisites
- GitHub account with access to this repository
- Render account (free tier works fine) - Sign up at https://render.com

### 2. Deploy to Render

#### Option A: Using Render Dashboard (Recommended)

1. **Log into Render**
   - Go to https://dashboard.render.com
   - Sign in or create a free account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"

3. **Connect Repository**
   - Choose "Connect a repository"
   - Authorize Render to access your GitHub
   - Select: `HARSH83022/AutoML-Agent-`
   - Branch: `Phase-4`

4. **Configure Service**
   - **Name**: `automl-platform` (or your preferred name)
   - **Region**: Choose closest to you
   - **Branch**: `Phase-4`
   - **Runtime**: Python 3
   - **Build Command**: 
     ```bash
     pip install --upgrade pip && pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && mkdir -p app/static && cp -r frontend/dist/* app/static/
     ```
   - **Start Command**:
     ```bash
     gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --timeout 600
     ```
   - **Instance Type**: Free

5. **Set Environment Variables**
   Click "Advanced" and add these environment variables:
   
   **Required:**
   - `APP_ENV` = `production`
   - `LOG_LEVEL` = `info`
   - `LLM_MODE` = `none`
   - `SYNTHETIC_DEFAULT_ROWS` = `1000`
   
   **Optional (for Kaggle dataset access):**
   - `KAGGLE_USERNAME` = `your_kaggle_username`
   - `KAGGLE_KEY` = `your_kaggle_api_key`
   
   **Optional (if using LLM features):**
   - `OPENAI_API_KEY` = `your_openai_key` (if using OpenAI)
   - `ANTHROPIC_API_KEY` = `your_anthropic_key` (if using Claude)
   - `GOOGLE_API_KEY` = `your_google_key` (if using Gemini)

6. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait 5-10 minutes for the first deployment

#### Option B: Using render.yaml (Infrastructure as Code)

The repository already includes a `render.yaml` file. Render will automatically detect it:

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render will read the `render.yaml` and configure everything automatically
5. Add environment variables in the dashboard (especially Kaggle credentials)

### 3. Verify Deployment

Once deployed, you'll get a URL like: `https://automl-platform.onrender.com`

**Test these endpoints:**
- `https://your-app.onrender.com/dashboard` - Main dashboard UI
- `https://your-app.onrender.com/runs` - List of runs (should return `{"runs": []}`)
- `https://your-app.onrender.com/checkllm` - Check LLM configuration

### 4. Using Your Deployed Application

1. **Access the Dashboard**
   - Open `https://your-app.onrender.com/dashboard`
   - You'll see the interactive AutoML interface

2. **Run AutoML Pipeline**
   - Choose whether you have a dataset or problem statement
   - Follow the interactive prompts
   - Monitor the run status in real-time

3. **API Access**
   - POST `/run` - Start a new AutoML run
   - GET `/status/{run_id}` - Check run status
   - GET `/runs` - List all runs
   - POST `/ps` - Interactive problem statement generation

## 📋 Configuration Details

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | Auto | - | Automatically set by Render |
| `APP_ENV` | Yes | production | Application environment |
| `LOG_LEVEL` | Yes | info | Logging level (debug/info/warning/error) |
| `LLM_MODE` | Yes | none | LLM provider (none/openai/anthropic/gemini/ollama) |
| `SYNTHETIC_DEFAULT_ROWS` | No | 1000 | Default rows for synthetic data |
| `KAGGLE_USERNAME` | No | - | Kaggle API username |
| `KAGGLE_KEY` | No | - | Kaggle API key |
| `OPENAI_API_KEY` | No | - | OpenAI API key (if LLM_MODE=openai) |
| `ANTHROPIC_API_KEY` | No | - | Anthropic API key (if LLM_MODE=anthropic) |
| `GOOGLE_API_KEY` | No | - | Google API key (if LLM_MODE=gemini) |

### Python Version

The application uses Python 3.11.9 (specified in `runtime.txt`)

### Dependencies

All dependencies are automatically installed from `requirements.txt` during build:
- FastAPI & Uvicorn (web framework)
- Gunicorn (production server)
- FLAML, XGBoost, LightGBM, CatBoost (AutoML)
- Pandas, NumPy, Scikit-learn (data processing)
- Transformers, HuggingFace (ML models)
- And more...

## 🔧 Troubleshooting

### Build Fails

**Error: "Could not find requirements.txt"**
- Solution: Make sure you're deploying from the `Phase-4` branch
- The `runtime.txt` file should be in the root directory

**Error: "Package installation failed"**
- Some ML packages (like LightGBM, CatBoost) require compilation
- Render's free tier should handle this, but it may take longer
- Check build logs for specific package errors

### Application Won't Start

**Error: "Application failed to bind to port"**
- Make sure the start command uses `$PORT` variable
- Current command: `gunicorn ... --bind 0.0.0.0:$PORT`

**Error: "Module not found"**
- Ensure all dependencies are in `requirements.txt`
- Check build logs to verify all packages installed successfully

### Runtime Errors

**Database errors**
- The app uses SQLite which is ephemeral on Render's free tier
- Data will be lost when the service restarts
- Consider upgrading to persistent storage if needed

**Out of memory**
- ML models can be memory-intensive
- Free tier has 512MB RAM
- Consider upgrading to a paid plan for larger models

### Slow Performance

**First request is slow**
- Render's free tier spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds to wake up
- Subsequent requests are fast
- Consider paid tier for always-on service

## 🔒 Security Best Practices

1. **Never commit API keys to the repository**
   - Use Render's environment variables
   - The `render.yaml` uses `sync: false` for sensitive variables

2. **Kaggle Credentials**
   - Set `KAGGLE_USERNAME` and `KAGGLE_KEY` in Render dashboard
   - Don't include them in `render.yaml`

3. **LLM API Keys**
   - Only add if you're using LLM features
   - Set in Render dashboard, not in code

## 📊 Monitoring

### Logs
- View logs in Render dashboard: Service → Logs tab
- Real-time log streaming available
- Search and filter logs by date/time

### Metrics
- CPU and Memory usage visible in dashboard
- Request count and response times
- Set up alerts for errors or downtime

## 🔄 Updates and Redeployment

### Automatic Deployment
- Render automatically deploys when you push to `Phase-4` branch
- Enable "Auto-Deploy" in service settings

### Manual Deployment
- Go to your service in Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"

### Rollback
- Go to "Events" tab in dashboard
- Click "Rollback" on any previous successful deployment

## 💰 Cost Considerations

### Free Tier Limits
- 750 hours/month of runtime
- 512MB RAM
- Shared CPU
- Spins down after 15 minutes of inactivity
- Perfect for development and testing

### Upgrading
- Starter: $7/month - 512MB RAM, always on
- Standard: $25/month - 2GB RAM, better performance
- Pro: $85/month - 4GB RAM, dedicated resources

## 📚 Additional Resources

- [Render Python Documentation](https://render.com/docs/deploy-fastapi)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render Build & Deploy](https://render.com/docs/deploys)
- [AutoML Agent GitHub Repository](https://github.com/HARSH83022/AutoML-Agent-)

## 🆘 Getting Help

If you encounter issues:
1. Check the build logs in Render dashboard
2. Review this troubleshooting guide
3. Check Render's status page: https://status.render.com
4. Contact Render support: https://render.com/support

---

**Your AutoML Agent is now deployed and ready to use! 🎉**

Access your application at: `https://your-service-name.onrender.com/dashboard`
