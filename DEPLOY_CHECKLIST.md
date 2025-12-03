# 🚀 Render Deployment Checklist

## ✅ Pre-Deployment (Complete These First)

- [ ] **1. GitHub Repository Ready**
  - [ ] Code is committed
  - [ ] Repository is public or Render has access
  - [ ] All files are pushed to `main` branch

- [ ] **2. Files Verified**
  - [x] `render.yaml` exists
  - [x] `requirements.txt` exists
  - [x] `app/main.py` exists
  - [x] `frontend/` folder exists
  - [x] `.gitignore` configured

- [ ] **3. Sensitive Data Protected**
  - [x] `.env` file is in `.gitignore`
  - [x] No API keys in code
  - [x] Kaggle credentials in `render.yaml` (encrypted by Render)

---

## 🎯 Deployment Steps

### Step 1: Push to GitHub
```bash
# Run this command:
cd automl-agent
./deploy_render.sh    # Linux/Mac
# OR
deploy_render.bat     # Windows
```

- [ ] Code pushed successfully
- [ ] No git errors

### Step 2: Create Render Service
1. [ ] Go to https://render.com
2. [ ] Sign in with GitHub
3. [ ] Click "New +" → "Web Service"
4. [ ] Select your repository
5. [ ] Render detects `render.yaml`
6. [ ] Click "Create Web Service"

### Step 3: Monitor Build
- [ ] Build starts automatically
- [ ] Python dependencies install (~5 min)
- [ ] Frontend builds (~3 min)
- [ ] Server starts successfully
- [ ] Health check passes

### Step 4: Test Deployment
- [ ] Visit your Render URL
- [ ] Homepage loads correctly
- [ ] Can create a new ML run
- [ ] Datasets load successfully
- [ ] Training completes

---

## 🔧 Post-Deployment

### Optional Configurations
- [ ] **Custom Domain**: Add your domain in Settings
- [ ] **Auto-Deploy**: Enable in Settings → Auto-Deploy
- [ ] **Monitoring**: Set up UptimeRobot to keep app awake
- [ ] **Alerts**: Configure email alerts for downtime

### Performance Optimization
- [ ] Test with small datasets first
- [ ] Monitor memory usage
- [ ] Check response times
- [ ] Consider upgrading plan if needed

---

## 📊 Your Deployment Info

**Service Name**: automl-platform
**Render URL**: https://automl-platform.onrender.com
**Plan**: Free (750 hours/month)
**Region**: Auto-selected

**Environment Variables**:
- ✅ KAGGLE_USERNAME
- ✅ KAGGLE_KEY
- ✅ LLM_MODE=none
- ✅ APP_ENV=production

---

## ⚠️ Common Issues & Solutions

### Issue: Build Fails
**Solution**: Check build logs in Render dashboard
- Verify Node.js version (18.x)
- Check Python version (3.11)
- Ensure all dependencies are in requirements.txt

### Issue: App Sleeps After 15 Minutes
**Solution**: Use UptimeRobot
1. Sign up at https://uptimerobot.com
2. Add monitor for your Render URL
3. Set interval to 10 minutes
4. App stays awake!

### Issue: Out of Memory
**Solution**: Reduce dataset size
- Edit `render.yaml`: `SYNTHETIC_DEFAULT_ROWS=500`
- Or upgrade to paid plan ($7/month)

### Issue: Slow First Request
**Solution**: This is normal on free tier
- App sleeps after 15 min inactivity
- First request wakes it up (~30 seconds)
- Subsequent requests are fast

---

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ Build completes without errors
- ✅ App is accessible at Render URL
- ✅ Homepage loads correctly
- ✅ Can create and run ML experiments
- ✅ Datasets download successfully
- ✅ Models train and return results

---

## 📞 Need Help?

**Render Documentation**: https://render.com/docs
**Render Community**: https://community.render.com
**Render Status**: https://status.render.com

**Your Deployment Guide**: See `RENDER_DEPLOY_GUIDE.md`

---

## ✅ Deployment Complete!

Once all checkboxes are checked, your AutoML Platform is live! 🚀

**Share your app**: https://automl-platform.onrender.com
