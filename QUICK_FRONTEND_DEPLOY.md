# Quick Frontend Deployment Guide

## 🚀 Deploy React Frontend in 5 Minutes

### Option 1: Manual Setup (Recommended)

1. **Go to Render**: https://dashboard.render.com

2. **Click "New +" → "Static Site"**

3. **Fill in these exact values:**
   ```
   Repository: HARSH83022/AutoML-Agent-
   Branch: Phase-4
   Name: automl-frontend
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

4. **Add Environment Variable:**
   ```
   VITE_API_URL = https://automl-platform-m1th.onrender.com
   ```

5. **Add Rewrite Rule (for React Router):**
   ```
   Source: /*
   Destination: /index.html
   Action: Rewrite
   ```

6. **Click "Create Static Site"**

7. **Done!** Your frontend will be live at: `https://automl-frontend.onrender.com`

### Option 2: Using Blueprint (Automatic)

1. **Go to Render**: https://dashboard.render.com

2. **Click "New +" → "Blueprint"**

3. **Connect repository**: `HARSH83022/AutoML-Agent-`

4. **Render will detect `render-frontend.yaml`**

5. **Click "Apply"**

6. **Done!** Everything configured automatically

## ✅ What You'll Get

**Frontend URL**: `https://automl-frontend.onrender.com`
- Modern React UI
- Fast loading (CDN)
- Client-side routing
- All AutoML features

**Backend URL**: `https://automl-platform-m1th.onrender.com`
- API endpoints
- Backup dashboard at `/dashboard`

## 🎯 After Deployment

Test your frontend:
1. Visit: `https://automl-frontend.onrender.com`
2. You should see the React UI
3. Try uploading a dataset
4. Generate a problem statement
5. Run AutoML!

## 💰 Cost

**FREE!** Static sites are free on Render.

## 🔧 Troubleshooting

**Build fails?**
- Check logs for npm errors
- Verify Node.js version (should be 18+)

**API calls fail?**
- Check `VITE_API_URL` is set correctly
- Open DevTools → Network tab
- Look for CORS errors

**Routes don't work?**
- Make sure rewrite rule is added
- Source: `/*` → Destination: `/index.html`

## 📚 Full Documentation

See `DEPLOY_FRONTEND_SEPARATELY.md` for detailed instructions.

---

**That's it! Your React frontend will be live in 5 minutes!** 🎉
