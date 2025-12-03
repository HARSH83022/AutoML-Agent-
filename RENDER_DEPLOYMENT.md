# 🚀 Deploy to Render - Complete Guide

## Quick Deploy (Automatic)

### Option 1: One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

Click the button above and Render will automatically:
1. Create backend and frontend services
2. Set up environment variables
3. Deploy your application
4. Provide you with live URLs

### Option 2: Deploy from GitHub

1. **Push your code to GitHub** (if not already)
   ```bash
   cd C:\Users\Dell\Desktop\Auto2\automl-agent
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/automl-agent.git
   git push -u origin main
   ```

2. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Sign up or log in

3. **Create New Blueprint**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and auto-configure

4. **Done!** Your app will be deployed automatically

---

## Manual Deployment (Step-by-Step)

### Step 1: Deploy Backend

1. **Go to Render Dashboard**
   - https://dashboard.render.com

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Or use "Deploy from Git URL"

3. **Configure Backend**
   ```
   Name: automl-backend
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   Plan: Starter ($7/month) or Free
   ```

4. **Add Environment Variables**
   Click "Environment" tab and add:
   ```
   LLM_MODE=ollama
   OLLAMA_MODEL=mistral:latest
   DATA_DIR=data
   ARTIFACT_DIR=artifacts
   SYNTHETIC_DEFAULT_ROWS=2000
   KAGGLE_USERNAME=your_username
   KAGGLE_KEY=your_api_key
   HF_TOKEN=your_hf_token
   ```

5. **Add Disk Storage** (Optional but recommended)
   - Go to "Disks" tab
   - Add disk: 10GB
   - Mount path: `/opt/render/project/src/data`

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your backend URL: `https://automl-backend.onrender.com`

### Step 2: Deploy Frontend

1. **Create Another Web Service**
   - Click "New +" → "Web Service"
   - Same repository

2. **Configure Frontend**
   ```
   Name: automl-frontend
   Region: Oregon (US West)
   Branch: main
   Root Directory: frontend
   Runtime: Node
   Build Command: npm install && npm run build
   Start Command: npm run preview -- --host 0.0.0.0 --port $PORT
   Plan: Starter or Free
   ```

3. **Add Environment Variable**
   ```
   VITE_API_URL=https://automl-backend.onrender.com
   ```
   (Use your actual backend URL from Step 1)

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (3-5 minutes)
   - Your frontend URL: `https://automl-frontend.onrender.com`

---

## Configuration Files

### render.yaml (Already Created)

The `render.yaml` file in your project root enables automatic deployment. It defines:
- Backend service configuration
- Frontend service configuration
- Environment variables
- Disk storage
- Auto-deploy settings

### Update Frontend API URL

After backend is deployed, update frontend to use the correct API URL:

**Option 1: Environment Variable (Recommended)**
Set in Render dashboard:
```
VITE_API_URL=https://your-backend-url.onrender.com
```

**Option 2: Update Code**
Edit `frontend/src/services/api.js`:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-backend-url.onrender.com/api'
```

---

## Environment Variables Reference

### Required Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `LLM_MODE` | `ollama` | LLM provider |
| `DATA_DIR` | `data` | Data storage directory |
| `ARTIFACT_DIR` | `artifacts` | Artifacts storage |

### Optional Variables

| Variable | Value | Description |
|----------|-------|-------------|
| `KAGGLE_USERNAME` | Your username | For Kaggle datasets |
| `KAGGLE_KEY` | Your API key | Kaggle API key |
| `HF_TOKEN` | Your token | HuggingFace token |
| `SYNTHETIC_DEFAULT_ROWS` | `2000` | Synthetic data rows |

### Get API Keys

**Kaggle:**
1. Go to https://www.kaggle.com/settings/account
2. Scroll to "API" section
3. Click "Create New Token"
4. Use username and key from downloaded file

**HuggingFace:**
1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Copy the token

---

## Post-Deployment

### 1. Verify Backend

Visit: `https://your-backend-url.onrender.com/docs`

You should see the FastAPI Swagger documentation.

### 2. Verify Frontend

Visit: `https://your-frontend-url.onrender.com`

You should see the AutoML platform homepage.

### 3. Test the Application

1. Click "Start New Run"
2. Generate or enter a problem statement
3. Start a training run
4. Check if it works end-to-end

---

## Troubleshooting

### Issue: Backend won't start

**Check logs:**
1. Go to Render dashboard
2. Click on your backend service
3. Go to "Logs" tab
4. Look for errors

**Common fixes:**
- Ensure `requirements.txt` is in root directory
- Check Python version (should be 3.11)
- Verify environment variables are set

### Issue: Frontend can't connect to backend

**Fix:**
1. Check `VITE_API_URL` environment variable
2. Ensure it points to your backend URL
3. Redeploy frontend after changing

**Check CORS:**
Backend should allow frontend origin. This is already configured in `app/main.py`.

### Issue: "Free instance will spin down"

**What it means:**
Free tier services sleep after 15 minutes of inactivity.

**Solutions:**
1. Upgrade to Starter plan ($7/month) - no sleep
2. Use a service like UptimeRobot to ping your app
3. Accept the 30-second cold start on first request

### Issue: Disk storage full

**Fix:**
1. Go to service → "Disks"
2. Increase disk size
3. Or clean up old artifacts:
   ```bash
   # In Render shell
   rm -rf artifacts/*_old.pkl
   ```

---

## Updating Your Deployment

### Automatic Updates

If you enabled auto-deploy:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Render will automatically redeploy!

### Manual Updates

1. Go to Render dashboard
2. Click your service
3. Click "Manual Deploy" → "Deploy latest commit"

---

## Monitoring

### View Logs

**Real-time logs:**
1. Go to service in dashboard
2. Click "Logs" tab
3. See live logs

**Download logs:**
Click "Download" button in logs view

### Metrics

Render provides:
- CPU usage
- Memory usage
- Request count
- Response times

Access in "Metrics" tab of your service.

### Alerts

Set up alerts:
1. Go to service settings
2. "Notifications" tab
3. Add email or Slack webhook

---

## Scaling

### Vertical Scaling (More Power)

1. Go to service settings
2. Change plan:
   - Free: 512MB RAM
   - Starter: 512MB RAM, no sleep
   - Standard: 2GB RAM
   - Pro: 4GB+ RAM

### Horizontal Scaling (More Instances)

Available on Pro plan and above:
1. Go to service settings
2. "Scaling" tab
3. Increase instance count

---

## Cost Estimation

### Free Tier
- **Cost:** $0/month
- **Limits:** 
  - 750 hours/month
  - Sleeps after 15 min inactivity
  - 512MB RAM

### Starter Plan
- **Cost:** $7/month per service
- **Benefits:**
  - No sleep
  - 512MB RAM
  - Custom domains

### For This Project
- Backend: $7/month (Starter)
- Frontend: $7/month (Starter)
- **Total: $14/month**

Or use Free tier for testing!

---

## Custom Domain (Optional)

### Add Custom Domain

1. Go to service settings
2. "Custom Domains" tab
3. Click "Add Custom Domain"
4. Enter your domain: `automl.yourdomain.com`
5. Add DNS records as shown:
   ```
   Type: CNAME
   Name: automl
   Value: your-service.onrender.com
   ```

### SSL Certificate

Render automatically provides free SSL certificates via Let's Encrypt!

---

## Backup Strategy

### Database Backup

Render doesn't auto-backup SQLite databases. Options:

**Option 1: Periodic Download**
```bash
# Download via Render shell
render shell automl-backend
tar -czf backup.tar.gz runs.db artifacts/
# Download from Render dashboard
```

**Option 2: External Storage**
Sync to S3/Google Cloud Storage periodically.

### Artifact Backup

Use disk storage and periodic backups to cloud storage.

---

## Security Best Practices

### 1. Environment Variables
- ✅ Store secrets in Render environment variables
- ❌ Never commit secrets to Git

### 2. HTTPS
- ✅ Render provides free SSL
- ✅ All traffic is encrypted

### 3. API Keys
- ✅ Rotate keys periodically
- ✅ Use separate keys for dev/prod

### 4. CORS
- ✅ Configure allowed origins
- ❌ Don't use `allow_origins=["*"]` in production

---

## Support & Resources

### Render Documentation
- https://render.com/docs

### Render Status
- https://status.render.com

### Community
- https://community.render.com

### This Project
- GitHub Issues: [your-repo]/issues
- Documentation: See other .md files

---

## Quick Reference

### Useful Commands

```bash
# View logs
render logs automl-backend

# Open shell
render shell automl-backend

# Restart service
render restart automl-backend

# Deploy manually
render deploy automl-backend
```

### Important URLs

- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Status: https://status.render.com

---

## Next Steps

After deployment:

1. ✅ Test all features
2. ✅ Set up monitoring
3. ✅ Configure custom domain (optional)
4. ✅ Set up backups
5. ✅ Share your app URL!

---

## Summary

**Deployment is easy:**
1. Push code to GitHub
2. Connect to Render
3. Deploy with one click
4. Your app is live!

**Your app will be at:**
- Frontend: `https://automl-frontend.onrender.com`
- Backend: `https://automl-backend.onrender.com`
- API Docs: `https://automl-backend.onrender.com/docs`

🎉 **Congratulations! Your AutoML platform is now live on the internet!**
