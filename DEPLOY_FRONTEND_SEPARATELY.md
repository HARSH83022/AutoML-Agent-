# Deploy React Frontend Separately on Render

## Why Separate Deployment?

Render's Python runtime doesn't include Node.js, so we can't build the React frontend during the Python service deployment. The solution is to deploy the frontend as a separate **Static Site** on Render.

## Architecture

```
Frontend (Static Site)  →  Backend (Web Service)
automl-frontend.onrender.com  →  automl-platform-m1th.onrender.com
```

## Step-by-Step Deployment

### 1. Deploy Frontend as Static Site

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com

2. **Create New Static Site**
   - Click "New +" → "Static Site"

3. **Connect Repository**
   - Select: `HARSH83022/AutoML-Agent-`
   - Branch: `Phase-4`

4. **Configure Build Settings**
   - **Name**: `automl-frontend`
   - **Root Directory**: Leave empty (or use `.`)
   - **Build Command**: 
     ```bash
     cd frontend && npm install && npm run build
     ```
   - **Publish Directory**: 
     ```
     frontend/dist
     ```

5. **Add Environment Variable**
   - Click "Advanced"
   - Add environment variable:
     - **Key**: `VITE_API_URL`
     - **Value**: `https://automl-platform-m1th.onrender.com`

6. **Configure Rewrites (for React Router)**
   - In "Redirects/Rewrites" section, add:
     - **Source**: `/*`
     - **Destination**: `/index.html`
     - **Action**: `Rewrite`

7. **Deploy**
   - Click "Create Static Site"
   - Wait 3-5 minutes for build

### 2. Update Backend CORS (Already Done!)

The backend already allows all origins with:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Test Your Deployment

Once deployed, you'll have:

**Frontend URL**: `https://automl-frontend.onrender.com`
- React UI
- Modern interface
- Client-side routing

**Backend URL**: `https://automl-platform-m1th.onrender.com`
- API endpoints
- Built-in dashboard at `/dashboard`

## Alternative: Use render.yaml Blueprint

I've created `render-frontend.yaml` in the repository. You can use Render's Blueprint feature:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect repository
4. Render will detect `render-frontend.yaml`
5. Click "Apply"

## Files Created

### 1. `frontend/.env.production`
```env
VITE_API_URL=https://automl-platform-m1th.onrender.com
```

### 2. `render-frontend.yaml`
```yaml
services:
  - type: web
    name: automl-frontend
    runtime: static
    branch: Phase-4
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: ./frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

## Troubleshooting

### Frontend Build Fails

**Check Node.js version:**
- Render uses Node 14 by default
- Your app needs Node 18+
- Add to environment variables: `NODE_VERSION=18`

**Check build logs:**
- Look for npm install errors
- Check if all dependencies are in package.json
- Verify vite.config.js is correct

### API Calls Fail

**Check CORS:**
- Backend must allow frontend origin
- Already configured with `allow_origins=["*"]`

**Check API URL:**
- Frontend uses `VITE_API_URL` environment variable
- Make sure it points to correct backend URL
- No trailing slash in URL

**Check Network Tab:**
- Open browser DevTools → Network
- See if API calls are going to correct URL
- Check for 404 or CORS errors

### React Router Not Working

**Add rewrite rule:**
- Source: `/*`
- Destination: `/index.html`
- This makes all routes serve index.html

## Cost

**Static Sites on Render:**
- ✅ **FREE** for static sites
- Unlimited bandwidth
- Global CDN
- Automatic HTTPS

**Total Cost:**
- Backend (Python): Free tier
- Frontend (Static): Free
- **Total: $0/month** 🎉

## Benefits of Separate Deployment

1. **✅ Works with Python runtime** - No Node.js needed in backend
2. **✅ Faster builds** - Frontend and backend build independently
3. **✅ Better caching** - Static files served from CDN
4. **✅ Easier updates** - Update frontend without redeploying backend
5. **✅ Free hosting** - Static sites are free on Render

## Next Steps

1. **Deploy frontend** following steps above
2. **Test the frontend** at your new URL
3. **Update any links** to point to new frontend URL
4. **Enjoy your React UI!** 🚀

---

**Your AutoML Agent will have:**
- ✅ Modern React frontend (separate static site)
- ✅ FastAPI backend (Python web service)
- ✅ Built-in dashboard (backup at `/dashboard`)
- ✅ All features working
- ✅ Free hosting for both!
