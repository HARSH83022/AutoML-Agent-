# ✅ Render Deployment Checklist

## Before You Start

- [ ] Code is working locally
- [ ] All changes are saved
- [ ] GitHub account created
- [ ] Render account created (https://render.com/register)

---

## Deployment Steps

### 1. Push to GitHub

- [ ] Open terminal in `C:\Users\Dell\Desktop\Auto2\automl-agent`
- [ ] Run: `git init`
- [ ] Run: `git add .`
- [ ] Run: `git commit -m "Initial commit"`
- [ ] Create repository on GitHub
- [ ] Run: `git remote add origin https://github.com/YOUR_USERNAME/automl-agent.git`
- [ ] Run: `git push -u origin main`

### 2. Deploy on Render

- [ ] Go to https://dashboard.render.com
- [ ] Click "New +" → "Blueprint"
- [ ] Connect GitHub repository
- [ ] Select `automl-agent` repository
- [ ] Click "Apply"

### 3. Configure Environment Variables

- [ ] Go to backend service
- [ ] Click "Environment" tab
- [ ] Add: `KAGGLE_USERNAME=ramyasharma10`
- [ ] Add: `KAGGLE_KEY=820ef1deeb71e11c4494e16cd071e921`
- [ ] Add: `HF_TOKEN=` (optional)

### 4. Wait for Deployment

- [ ] Backend deploys (5-10 minutes)
- [ ] Frontend deploys (3-5 minutes)
- [ ] Both show "Live" status

### 5. Update Frontend API URL

- [ ] Copy backend URL from Render
- [ ] Go to frontend service
- [ ] Environment tab
- [ ] Update `VITE_API_URL` to backend URL
- [ ] Redeploy frontend

### 6. Test Your App

- [ ] Visit frontend URL
- [ ] Click "Start New Run"
- [ ] Generate problem statement
- [ ] Start a run
- [ ] Check if it completes successfully

---

## Your URLs

After deployment, save these:

- **Frontend:** `https://automl-frontend.onrender.com`
- **Backend:** `https://automl-backend.onrender.com`
- **API Docs:** `https://automl-backend.onrender.com/docs`

---

## Troubleshooting

### Build Failed?
- [ ] Check logs in Render dashboard
- [ ] Verify `requirements.txt` exists
- [ ] Check Python/Node versions

### App Not Starting?
- [ ] Check environment variables
- [ ] Check start command
- [ ] Review error logs

### Frontend Can't Connect?
- [ ] Verify `VITE_API_URL` is set
- [ ] Check backend is running
- [ ] Test backend URL directly

---

## Success Indicators

✅ Backend shows "Live" in dashboard
✅ Frontend shows "Live" in dashboard
✅ Can access frontend URL in browser
✅ Can access backend /docs endpoint
✅ Can create and run ML tasks
✅ Run completes successfully

---

## Next Steps

- [ ] Share your app URL with others
- [ ] Set up custom domain (optional)
- [ ] Configure monitoring/alerts
- [ ] Set up backups
- [ ] Upgrade to paid plan (no sleep)

---

## Quick Commands

```bash
# Push updates
git add .
git commit -m "Update"
git push origin main

# Render will auto-deploy!
```

---

## Cost

**Free Tier:** $0 (sleeps after 15 min)
**Starter:** $14/month (no sleep, better performance)

---

## Help

- **Render Docs:** https://render.com/docs
- **Detailed Guide:** See `RENDER_DEPLOYMENT.md`
- **Quick Start:** See `deploy_to_render.md`

---

**Ready to deploy? Follow the checklist above!** 🚀
