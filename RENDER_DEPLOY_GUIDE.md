# 🚀 Render Deployment Guide - AutoML Platform

## ✅ Pre-Deployment Checklist

### 1. **Verify Your Files**
- [x] `render.yaml` - Render configuration
- [x] `requirements.txt` - Python dependencies
- [x] `.gitignore` - Excludes sensitive files
- [x] `app/main.py` - FastAPI backend
- [x] `frontend/` - React frontend

### 2. **Environment Variables Ready**
- [x] `KAGGLE_USERNAME` = harsh83022
- [x] `KAGGLE_KEY` = 04bd6ce5bcb813d98f2a83457af5c44a
- [x] `LLM_MODE` = none (no LLM required)

---

## 🎯 Deployment Steps

### **Step 1: Prepare Your Repository**

#### Option A: If you have a GitHub repo
```bash
cd automl-agent

# Add all files
git add .

# Commit changes
git commit -m "Ready for Render deployment"

# Push to GitHub
git push origin main
```

#### Option B: Create a new GitHub repo
```bash
cd automl-agent

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - AutoML Platform"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/automl-platform.git
git branch -M main
git push -u origin main
```

---

### **Step 2: Deploy on Render**

1. **Go to Render Dashboard**
   - Visit: https://render.com
   - Sign in with GitHub

2. **Create New Web Service**
   - Click **"New +"** button
   - Select **"Web Service"**

3. **Connect Repository**
   - Click **"Connect a repository"**
   - Authorize Render to access your GitHub
   - Select your `automl-platform` repository

4. **Configure Service**
   Render will auto-detect your `render.yaml` file:
   
   - **Name**: `automl-platform`
   - **Runtime**: Python 3
   - **Build Command**: (auto-filled from render.yaml)
   - **Start Command**: (auto-filled from render.yaml)
   - **Plan**: Free

5. **Review Environment Variables**
   These are already in `render.yaml`:
   ```
   KAGGLE_USERNAME = harsh83022
   KAGGLE_KEY = 04bd6ce5bcb813d98f2a83457af5c44a
   LLM_MODE = none
   APP_ENV = production
   ```

6. **Deploy**
   - Click **"Create Web Service"**
   - Render will start building your app
   - Build time: ~10-15 minutes (first time)

---

### **Step 3: Monitor Deployment**

#### Watch Build Logs
```
Building...
├── Installing Python dependencies
├── Building React frontend
├── Copying static files
└── Starting server
```

#### Check for Success
- ✅ Build completes without errors
- ✅ Server starts successfully
- ✅ Health check passes

---

## 🌐 Access Your App

Once deployed, Render provides a URL:
```
https://automl-platform.onrender.com
```

### Test Your Deployment
1. Visit the URL
2. You should see the AutoML Platform homepage
3. Try creating a new ML run
4. Check that datasets are loading

---

## 🔧 Post-Deployment Configuration

### Optional: Add Custom Domain
1. Go to **Settings** → **Custom Domain**
2. Add your domain (e.g., `automl.yourdomain.com`)
3. Update DNS records as instructed

### Optional: Enable Auto-Deploy
- **Settings** → **Auto-Deploy**: ON
- Every push to `main` branch will auto-deploy

### Optional: Add More Environment Variables
If you want to enable LLM features later:
```bash
# In Render Dashboard → Environment
OPENAI_API_KEY = your_openai_key
LLM_MODE = openai
```

---

## 📊 Monitoring & Logs

### View Logs
1. Go to your service dashboard
2. Click **"Logs"** tab
3. See real-time application logs

### Check Metrics
- **Metrics** tab shows:
  - CPU usage
  - Memory usage
  - Request count
  - Response times

### Health Check
Your app has a health endpoint:
```
GET https://automl-platform.onrender.com/health
```

---

## ⚠️ Important Notes

### Free Tier Limitations
- **Sleep after 15 min inactivity**
  - First request after sleep takes ~30 seconds
  - Solution: Use a service like UptimeRobot to ping every 10 min

- **750 hours/month free**
  - Enough for development/testing
  - Upgrade to paid plan for production

- **512 MB RAM**
  - Sufficient for small datasets
  - May need upgrade for large ML workloads

### Performance Tips
1. **Keep app awake**: Use cron job to ping every 10 minutes
2. **Optimize dataset size**: Limit to 10,000 rows on free tier
3. **Reduce training time**: Set `training_budget_minutes` to 2-3

---

## 🐛 Troubleshooting

### Build Fails
**Problem**: Frontend build fails
```bash
# Solution: Check Node.js version
# Ensure render.yaml has: NODE_VERSION=18.x
```

**Problem**: Python dependencies fail
```bash
# Solution: Check requirements.txt
# Ensure all packages are compatible
```

### App Crashes
**Problem**: Out of memory
```bash
# Solution: Reduce dataset size or upgrade plan
# Add to render.yaml:
envVars:
  - key: SYNTHETIC_DEFAULT_ROWS
    value: 500  # Reduce from 1000
```

**Problem**: Timeout errors
```bash
# Solution: Already configured with 600s timeout
# Check logs for specific errors
```

### Can't Access App
**Problem**: 404 errors
```bash
# Solution: Ensure static files are built
# Check build logs for frontend build success
```

**Problem**: API errors
```bash
# Solution: Check environment variables
# Verify KAGGLE credentials are set
```

---

## 🔄 Updating Your App

### Deploy Updates
```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin main

# Render auto-deploys (if enabled)
# Or manually trigger deploy in dashboard
```

### Rollback
If something breaks:
1. Go to **Deploys** tab
2. Find previous working deploy
3. Click **"Rollback to this version"**

---

## 📞 Support

### Render Support
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### Your App Logs
```bash
# View logs in real-time
# Render Dashboard → Logs tab
```

---

## ✅ Deployment Complete!

Your AutoML Platform is now live on Render! 🎉

**Next Steps:**
1. Test all features
2. Share the URL with users
3. Monitor performance
4. Consider upgrading plan for production use

**Your App URL:**
```
https://automl-platform.onrender.com
```

---

## 🚀 Quick Commands Reference

```bash
# Push updates
git add .
git commit -m "Your message"
git push origin main

# View logs (from Render dashboard)
# Settings → Logs

# Restart service (from Render dashboard)
# Manual Deploy → Deploy latest commit

# Check health
curl https://automl-platform.onrender.com/health
```

---

**Happy Deploying! 🚀**
