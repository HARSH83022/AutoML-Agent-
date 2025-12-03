# 🚀 Deploy to Render (No Credit Card Required!)

## ✅ **Why Render?**
- ✅ **No credit card required**
- ✅ **Free tier available**
- ✅ **Simpler than Azure**
- ✅ **Deploy in 10 minutes**
- ✅ **Perfect for testing**

---

## 📝 **Step-by-Step Deployment**

### **Step 1: Create Render Account**

1. Go to: **https://render.com/register**
2. Sign up with:
   - GitHub (recommended)
   - Or email: `harshmishra83022@gmail.com`
3. Verify your email
4. **Done!** No credit card needed

---

### **Step 2: Push Code to GitHub (If Not Already)**

```powershell
cd C:\Users\Dell\Desktop\Auto2\automl-agent

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create GitHub repo and push
# (Or use GitHub Desktop)
```

**Or use GitHub Desktop:**
1. Open GitHub Desktop
2. Add repository: `C:\Users\Dell\Desktop\Auto2\automl-agent`
3. Commit changes
4. Publish to GitHub

---

### **Step 3: Create Web Service on Render**

1. **Login to Render**: https://dashboard.render.com
2. **Click**: "New +" button (top right)
3. **Select**: "Web Service"
4. **Connect GitHub**:
   - Click "Connect GitHub"
   - Authorize Render
   - Select your repository
5. **Click**: "Connect" next to your repo

---

### **Step 4: Configure Service**

Fill in these settings:

**Basic Settings:**
- **Name**: `automl-platform` (or any name you like)
- **Region**: `Oregon (US West)` or closest to you
- **Branch**: `main` or `master`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select: **Free** (0.1 CPU, 512 MB RAM)

---

### **Step 5: Add Environment Variables**

Scroll down to "Environment Variables" section and add:

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `LOG_LEVEL` | `info` |
| `KAGGLE_USERNAME` | `harsh83022` |
| `KAGGLE_KEY` | `04bd6ce5bcb813d98f2a83457af5c44a` |
| `LLM_MODE` | `none` |
| `SYNTHETIC_DEFAULT_ROWS` | `1000` |
| `PYTHON_VERSION` | `3.11.0` |

**Click**: "Add" for each variable

---

### **Step 6: Deploy!**

1. **Click**: "Create Web Service" (bottom of page)
2. **Wait**: 5-10 minutes for deployment
3. **Watch**: Build logs in real-time
4. **Done**: You'll see "Your service is live!"

---

### **Step 7: Get Your URL**

After deployment:
- Your app URL: `https://automl-platform-xxxx.onrender.com`
- Copy this URL!

**Test it:**
- Main page: `https://your-app.onrender.com`
- API docs: `https://your-app.onrender.com/docs`
- Health check: `https://your-app.onrender.com/health`

---

## 🎯 **Quick Configuration File**

Create `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: automl-platform
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: APP_ENV
        value: production
      - key: KAGGLE_USERNAME
        value: harsh83022
      - key: KAGGLE_KEY
        value: 04bd6ce5bcb813d98f2a83457af5c44a
      - key: LLM_MODE
        value: none
      - key: PYTHON_VERSION
        value: 3.11.0
```

Then just:
1. Push to GitHub
2. Connect to Render
3. Render will auto-detect the config
4. Click "Apply"

---

## 💰 **Render Free Tier**

**What you get for FREE:**
- ✅ 750 hours/month (enough for 24/7 uptime)
- ✅ 512 MB RAM
- ✅ 0.1 CPU
- ✅ Automatic SSL
- ✅ Custom domains
- ✅ Automatic deploys from GitHub

**Limitations:**
- Spins down after 15 min of inactivity
- First request after spin-down takes ~30 seconds
- Limited compute power

**Perfect for:**
- Testing and demos
- Personal projects
- Low-traffic apps

---

## 🔄 **Auto-Deploy from GitHub**

Once connected, Render will:
- ✅ Auto-deploy on every push to main branch
- ✅ Show build logs
- ✅ Rollback if deployment fails
- ✅ Keep previous versions

**To update your app:**
```powershell
git add .
git commit -m "Update"
git push
```

Render will automatically redeploy!

---

## 📊 **Monitor Your App**

**Render Dashboard:**
- View logs: Real-time application logs
- Metrics: CPU, memory, requests
- Events: Deployment history
- Settings: Update environment variables

**Access logs:**
1. Go to Render Dashboard
2. Click your service
3. Click "Logs" tab
4. See real-time logs

---

## 🐛 **Troubleshooting**

### **Build Failed**
- Check `requirements.txt` is correct
- View build logs for errors
- Ensure Python version is 3.11

### **App Won't Start**
- Check start command is correct
- View logs for errors
- Verify environment variables

### **App is Slow**
- Free tier spins down after 15 min
- First request takes ~30 seconds
- Upgrade to paid tier ($7/month) for always-on

### **502 Bad Gateway**
- App is starting up (wait 30 seconds)
- Or app crashed (check logs)

---

## 🚀 **Upgrade Options**

**Starter Plan ($7/month):**
- Always on (no spin-down)
- 512 MB RAM
- 0.5 CPU
- Faster response times

**Standard Plan ($25/month):**
- 2 GB RAM
- 1 CPU
- Better performance

---

## ✅ **Deployment Checklist**

- [ ] Create Render account
- [ ] Push code to GitHub
- [ ] Connect GitHub to Render
- [ ] Configure service settings
- [ ] Add environment variables
- [ ] Deploy service
- [ ] Test app URL
- [ ] Check API docs
- [ ] Verify Kaggle integration

---

## 🎉 **You're Done!**

Your AutoML platform is now live on Render!

**Your app URL**: `https://automl-platform-xxxx.onrender.com`

**Next steps:**
1. Test the API
2. Create a test ML run
3. Share your app URL
4. Monitor logs and metrics

---

## 📞 **Support**

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Render Status**: https://status.render.com

**Good luck!** 🚀
