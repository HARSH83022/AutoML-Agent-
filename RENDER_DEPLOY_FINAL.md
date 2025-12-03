# 🚀 Deploy to Render - Final Guide

## ✅ Prerequisites
- [x] GitHub repo with Phase-4 branch
- [x] Dockerfile removed (renamed to Dockerfile.backup)
- [x] render.yaml configured
- [ ] Render account (free)

---

## 📝 Step 1: Create Render Account

1. Go to: https://render.com
2. Click "Get Started"
3. Sign up with GitHub (easiest)
4. Authorize Render to access your repositories

---

## 🗑️ Step 2: Delete Old Service (If Exists)

If you already created a service:
1. Go to: https://dashboard.render.com
2. Find your service in the list
3. Click on it
4. Settings (bottom left) → Scroll down
5. Click "Delete Web Service"
6. Confirm deletion

---

## 🆕 Step 3: Create New Web Service

### **3.1 Start Creation**
1. Go to: https://dashboard.render.com
2. Click **"New +"** (top right)
3. Select **"Web Service"**

### **3.2 Connect Repository**
1. Click **"Build and deploy from a Git repository"**
2. Click **"Next"**
3. Find **"AutoML-Agent-"** in the list
4. Click **"Connect"**

### **3.3 Configure Service**

Fill in these EXACT values:

**Name:**
```
automl-platform
```

**Region:**
```
Oregon (US West)
```
(or choose closest to you)

**Branch:**
```
Phase-4
```

**Root Directory:**
```
(leave blank)
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && mkdir -p app/static && cp -r frontend/dist/* app/static/
```

**Start Command:**
```
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --timeout 600
```

**Instance Type:**
```
Free
```

---

## 🔐 Step 4: Add Environment Variables

Click **"Advanced"** button, then add these one by one:

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `LOG_LEVEL` | `info` |
| `KAGGLE_USERNAME` | `harsh83022` |
| `KAGGLE_KEY` | `04bd6ce5bcb813d98f2a83457af5c44a` |
| `LLM_MODE` | `none` |
| `SYNTHETIC_DEFAULT_ROWS` | `1000` |
| `PYTHON_VERSION` | `3.11.0` |
| `NODE_VERSION` | `18.x` |

**How to add each variable:**
1. Click "Add Environment Variable"
2. Enter Key in first box
3. Enter Value in second box
4. Repeat for all 8 variables

---

## 🎯 Step 5: Create Service

1. Review all settings
2. Click **"Create Web Service"** (bottom)
3. Wait for deployment (10-15 minutes)

---

## ⏱️ What Happens During Deployment

You'll see these stages:

1. **Cloning repository** (30 seconds)
   - Fetching code from GitHub
   
2. **Installing Python dependencies** (2-3 minutes)
   - Installing packages from requirements.txt
   
3. **Building frontend** (3-5 minutes)
   - Installing npm packages
   - Building React app
   
4. **Copying files** (30 seconds)
   - Moving frontend build to static folder
   
5. **Starting server** (1 minute)
   - Starting Gunicorn with Uvicorn workers
   
6. **Health checks** (1 minute)
   - Verifying app is responding

**Total time: 10-15 minutes**

---

## ✅ Step 6: Verify Deployment

Once you see "Live" with a green dot:

1. Click on the URL at the top (looks like: `https://automl-platform.onrender.com`)
2. Your app should load!

**Test these endpoints:**
- Main app: `https://your-app.onrender.com`
- API docs: `https://your-app.onrender.com/docs`
- Health check: `https://your-app.onrender.com/health`

---

## 🐛 Troubleshooting

### Issue: Build fails with "npm: command not found"

**Solution:** Render needs Node.js for the frontend build. Make sure:
- `NODE_VERSION=18.x` is in environment variables
- Build command includes `cd frontend && npm install`

### Issue: Build fails with "No module named 'app'"

**Solution:** Check that:
- Root Directory is blank (not set to "automl-agent")
- Start command uses `app.main:app` (not `automl-agent.app.main:app`)

### Issue: App shows "Application failed to respond"

**Solution:**
1. Check logs (click "Logs" tab)
2. Look for errors
3. Common fixes:
   - Wait 2-3 minutes for full startup
   - Check environment variables are set correctly
   - Verify PORT is not hardcoded (use `$PORT`)

### Issue: Frontend shows but API doesn't work

**Solution:**
- Check that frontend was built correctly
- Look in logs for "Copying frontend build"
- Verify `app/static` folder was created

---

## 📊 Monitor Your App

### View Logs
1. Go to your service dashboard
2. Click "Logs" tab
3. See real-time logs

### View Metrics
1. Click "Metrics" tab
2. See CPU, memory, response times

### Restart App
1. Click "Manual Deploy" dropdown
2. Select "Clear build cache & deploy"

---

## 💰 Cost

**Free Tier:**
- 750 hours/month (enough for 24/7)
- Spins down after 15 min of inactivity
- Spins up automatically when accessed (30 sec delay)
- **Cost: $0/month**

**Paid Tier ($7/month):**
- Always on (no spin down)
- Faster
- More resources

---

## 🎯 Quick Reference

**Your GitHub Repo:**
```
https://github.com/HARSH83022/AutoML-Agent-
```

**Branch:**
```
Phase-4
```

**Build Command:**
```
pip install --upgrade pip && pip install -r requirements.txt && cd frontend && npm install && npm run build && cd .. && mkdir -p app/static && cp -r frontend/dist/* app/static/
```

**Start Command:**
```
gunicorn -w 2 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:$PORT --timeout 600
```

**Environment Variables:**
```
APP_ENV=production
LOG_LEVEL=info
KAGGLE_USERNAME=harsh83022
KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a
LLM_MODE=none
SYNTHETIC_DEFAULT_ROWS=1000
PYTHON_VERSION=3.11.0
NODE_VERSION=18.x
```

---

## ✅ Deployment Checklist

- [ ] Render account created
- [ ] Old Docker service deleted (if exists)
- [ ] New Web Service created
- [ ] Repository connected (AutoML-Agent-)
- [ ] Branch set to Phase-4
- [ ] Runtime set to Python 3
- [ ] Build command entered
- [ ] Start command entered
- [ ] All 8 environment variables added
- [ ] Instance type set to Free
- [ ] Clicked "Create Web Service"
- [ ] Waited 10-15 minutes
- [ ] App shows "Live" status
- [ ] Tested main URL
- [ ] Tested /docs endpoint
- [ ] Tested /health endpoint

---

## 🎉 Success!

Once deployed, your AutoML platform will be live at:
```
https://automl-platform.onrender.com
```

Share this URL with anyone - your app is now publicly accessible!

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Check logs in Render dashboard for errors

**Good luck with your deployment!** 🚀
