# 🚀 Quick Deploy to Render

## Prerequisites
- GitHub account
- Render account (free): https://render.com/register

---

## 🎯 3-Step Deployment

### Step 1: Push to GitHub

```bash
cd C:\Users\Dell\Desktop\Auto2\automl-agent

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "AutoML Platform - Ready for deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/automl-agent.git
git branch -M main
git push -u origin main
```

### Step 2: Connect to Render

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Click "Connect GitHub"
4. Select your `automl-agent` repository
5. Render will detect `render.yaml` automatically
6. Click "Apply"

### Step 3: Configure Secrets

In Render dashboard, add these environment variables:

**For Backend Service:**
```
KAGGLE_USERNAME=ramyasharma10
KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921
HF_TOKEN=(optional - your HuggingFace token)
```

**Done!** Your app will deploy automatically.

---

## 🌐 Access Your App

After deployment (5-10 minutes):

- **Frontend:** `https://automl-frontend.onrender.com`
- **Backend API:** `https://automl-backend.onrender.com`
- **API Docs:** `https://automl-backend.onrender.com/docs`

---

## ⚙️ Alternative: Manual Deployment

### Deploy Backend Only

1. **New Web Service**
   - Name: `automl-backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Environment Variables:**
   ```
   LLM_MODE=ollama
   DATA_DIR=data
   ARTIFACT_DIR=artifacts
   KAGGLE_USERNAME=ramyasharma10
   KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921
   ```

3. **Deploy** and note the URL

### Deploy Frontend

1. **New Web Service**
   - Name: `automl-frontend`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Start Command: `npm run preview -- --host 0.0.0.0 --port $PORT`

2. **Environment Variable:**
   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   ```

3. **Deploy**

---

## 🔧 Troubleshooting

### Build Fails

**Check logs in Render dashboard**

Common issues:
- Missing dependencies → Check `requirements.txt`
- Python version → Ensure Python 3.11
- Node version → Ensure Node 18+

### App Won't Start

**Check:**
1. Environment variables are set
2. Start command is correct
3. Port is set to `$PORT` (Render provides this)

### Frontend Can't Connect

**Fix:**
1. Update `VITE_API_URL` to your backend URL
2. Redeploy frontend
3. Check CORS settings in backend

---

## 💰 Cost

### Free Tier
- **Cost:** $0
- **Limits:** Sleeps after 15 min inactivity
- **Good for:** Testing, demos

### Starter Plan
- **Cost:** $7/month per service
- **Benefits:** No sleep, better performance
- **Total:** $14/month (backend + frontend)

---

## 📊 Monitor Your App

### View Logs
1. Go to service in dashboard
2. Click "Logs" tab
3. See real-time logs

### Check Metrics
1. Click "Metrics" tab
2. See CPU, memory, requests

### Set Alerts
1. Go to "Notifications"
2. Add email or Slack webhook

---

## 🎉 Success!

Once deployed, share your app:
- **Your App:** `https://automl-frontend.onrender.com`
- **API Docs:** `https://automl-backend.onrender.com/docs`

Anyone can access it! 🌍

---

## 🔄 Updates

To update your deployed app:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main
```

Render will automatically redeploy! ✨

---

## Need Help?

- **Render Docs:** https://render.com/docs
- **Render Community:** https://community.render.com
- **This Project:** See `RENDER_DEPLOYMENT.md` for detailed guide
