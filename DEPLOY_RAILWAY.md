# Railway Deployment Guide

## Automatic Deployment Setup

Railway automatically deploys your application when you push to GitHub. Here's how to ensure it's working:

### 1. Initial Setup (One-Time)

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Create New Project** → "Deploy from GitHub repo"
3. **Select Repository**: `HARSH83022/AutoML-Agent-`
4. **Railway will automatically**:
   - Detect the Dockerfile
   - Start building the image
   - Deploy the container

### 2. Configure Environment Variables

In the Railway dashboard, go to your project → Variables tab and add:

```bash
# Required
PORT=8000  # Railway will override this automatically

# LLM Configuration (choose one)
LLM_MODE=none  # or openai, anthropic, gemini

# Optional: If using OpenAI
# OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4-turbo-preview

# Optional: If using Anthropic
# ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Optional: If using Google Gemini
# GOOGLE_API_KEY=...
# GEMINI_MODEL=gemini-2.0-flash-exp

# Kaggle Integration
KAGGLE_USERNAME=harsh83022
KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a

# Application Settings
SYNTHETIC_DEFAULT_ROWS=1000
THREAD_POOL_SIZE=2
```

### 3. Automatic Deployment

Once connected, Railway will automatically:

✅ **Deploy on every push to main branch**
- Push code → Railway detects changes → Builds → Deploys

✅ **Provide a public URL**
- Format: `https://your-app-name.up.railway.app`
- Find it in: Project → Settings → Domains

✅ **Show build logs**
- View in: Project → Deployments → Click on deployment

### 4. Manual Redeploy (if needed)

If automatic deployment doesn't trigger:

1. Go to Railway Dashboard
2. Select your project
3. Click "Deployments" tab
4. Click "Deploy" button (top right)
5. Select "Redeploy"

### 5. Check Deployment Status

**View Logs**:
```
Railway Dashboard → Your Project → Deployments → Latest Deployment → View Logs
```

**Check if running**:
```bash
curl https://your-app-name.up.railway.app/health
```

Should return:
```json
{"status": "ok"}
```

### 6. Access Your Application

Once deployed, access:
- **Dashboard**: `https://your-app-name.up.railway.app/dashboard`
- **API Docs**: `https://your-app-name.up.railway.app/docs`
- **Health Check**: `https://your-app-name.up.railway.app/health`

## Troubleshooting

### Build Fails

**Check build logs** in Railway dashboard:
- Look for Python dependency errors
- Check if frontend build succeeded
- Verify Dockerfile syntax

**Common fixes**:
```bash
# Clear Railway cache
Railway Dashboard → Settings → Clear Build Cache → Redeploy
```

### Container Crashes

**Check runtime logs**:
```
Railway Dashboard → Deployments → View Logs
```

**Common issues**:
- Missing environment variables
- Port binding errors (should be fixed with start.py)
- Out of memory (upgrade Railway plan)

### Application Not Responding

1. **Check if container is running**:
   - Railway Dashboard → Deployments → Status should be "Active"

2. **Check health endpoint**:
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```

3. **Check logs for errors**:
   - Look for startup errors
   - Check if uvicorn started successfully

### PORT Variable Issues

The latest fix uses `start.py` which properly reads the PORT variable:
```python
port = os.environ.get("PORT", "8000")
```

If you still see PORT errors:
1. Check Railway logs for the actual error
2. Verify start.py is being executed
3. Check if Railway is setting the PORT variable

## Monitoring

### View Metrics

Railway Dashboard → Your Project → Metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count

### Set Up Alerts

Railway Dashboard → Settings → Notifications:
- Deployment failures
- Container crashes
- Resource limits

## Updating Your Application

### Automatic Updates

1. Make changes locally
2. Commit: `git commit -m "Your changes"`
3. Push: `git push origin main`
4. Railway automatically detects and deploys

### Rollback

If deployment fails:

1. Railway Dashboard → Deployments
2. Find previous working deployment
3. Click "..." → "Redeploy"

## Cost Management

### Free Tier Limits

Railway free tier includes:
- $5 credit per month
- 500 hours of usage
- 1GB RAM
- 1 vCPU

### Monitor Usage

Railway Dashboard → Usage:
- Check remaining credits
- View resource consumption
- Upgrade if needed

## Advanced Configuration

### Custom Domain

1. Railway Dashboard → Settings → Domains
2. Click "Add Domain"
3. Enter your domain
4. Configure DNS records as shown

### Environment-Specific Variables

Create different environments:
1. Railway Dashboard → Settings → Environments
2. Add "staging" or "production"
3. Set different variables per environment

### Persistent Storage (if needed)

For database and artifacts:
1. Railway Dashboard → Add Service → Volume
2. Mount path: `/app/artifacts` and `/app/data`
3. Redeploy application

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **GitHub Issues**: https://github.com/HARSH83022/AutoML-Agent-/issues

## Quick Commands

```bash
# Check deployment status
curl https://your-app-name.up.railway.app/health

# View recent runs
curl https://your-app-name.up.railway.app/runs

# Test API
curl -X POST https://your-app-name.up.railway.app/run \
  -H "Content-Type: application/json" \
  -d '{"problem_statement": "Predict house prices"}'
```

## Next Steps

1. ✅ Code is pushed to GitHub
2. ✅ Dockerfile is configured
3. ✅ start.py handles PORT variable
4. 🔄 Railway should auto-deploy now
5. ⏳ Wait for build to complete (5-10 minutes)
6. ✅ Access your application at the Railway URL

**Your deployment should be automatic now!** Check the Railway dashboard to see the build progress.
