# Troubleshooting Guide

## Issue: Run Not Starting After Selecting Problem Statement

### Quick Fix

I've just fixed the API communication issue. The frontend was sending data in the wrong format. 

**To apply the fix:**

1. **Stop the frontend** (Ctrl+C in the frontend terminal)
2. **Restart the frontend:**
   ```bash
   cd automl-agent/frontend
   npm run dev
   ```
3. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
4. **Try again**

---

## How to Verify Frontend-Backend Connection

### Step 1: Check Backend is Running

Open browser and go to: **http://localhost:8000/docs**

You should see the FastAPI Swagger documentation page. If not:
- Backend is not running
- Start it with: `python start_server.py`

### Step 2: Check Frontend is Running

Your frontend terminal should show:
```
  VITE v5.x.x  ready in xxx ms
  ➜  Local:   http://localhost:3000/
```

If you see port 5173 instead of 3000, that's fine - just use that port.

### Step 3: Test API Connection

Open browser console (F12) and run:
```javascript
fetch('/api/runs')
  .then(r => r.json())
  .then(d => console.log('API Response:', d))
  .catch(e => console.error('API Error:', e))
```

**Expected result:** You should see `{runs: [...]}`

**If you see an error:**
- Check backend is running on port 8000
- Check frontend proxy configuration
- Check browser console for CORS errors

---

## Common Issues and Solutions

### Issue 1: "Failed to start run" Error

**Symptoms:**
- Click "Start Run" button
- Nothing happens or error message appears
- No navigation to run details page

**Solutions:**

1. **Check Browser Console (F12 → Console tab)**
   Look for errors like:
   - `Failed to fetch` → Backend not running
   - `404 Not Found` → Wrong API endpoint
   - `422 Unprocessable Entity` → Wrong data format (should be fixed now)

2. **Check Backend Terminal**
   Look for:
   - Error messages
   - No log entries → Request not reaching backend

3. **Verify API Format**
   The backend expects:
   ```json
   {
     "problem_statement": "Your PS here",
     "preferences": {
       "training_budget_minutes": 5,
       "primary_metric": "f1"
     },
     "user": {}
   }
   ```

### Issue 2: CORS Errors

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/run' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Solution:**
The backend should have CORS enabled. Check `main.py` has:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If not, add this after `app = FastAPI(...)` line.

### Issue 3: Port Already in Use

**Backend Error:**
```
ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000)
```

**Solution:**
```bash
# Windows - Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

**Frontend Error:**
```
Port 3000 is in use, trying another one...
```

**Solution:** Vite will automatically use next available port (3001, 3002, etc.)

### Issue 4: Module Not Found Errors

**Backend:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
cd automl-agent
pip install -r requirements.txt
```

**Frontend:**
```
Cannot find module 'react'
```

**Solution:**
```bash
cd automl-agent/frontend
npm install
```

### Issue 5: Database Locked Error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
# Stop backend
# Delete database file
del runs.db        # Windows
rm runs.db         # Mac/Linux
# Restart backend
```

---

## Debugging Steps

### 1. Test Backend Directly

Use curl or Postman to test the `/run` endpoint:

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "problem_statement": "Predict house prices",
    "preferences": {"training_budget_minutes": 1},
    "user": {}
  }'
```

**Expected response:**
```json
{
  "run_id": "some-uuid-here",
  "status": "queued"
}
```

### 2. Check Network Tab

1. Open browser DevTools (F12)
2. Go to Network tab
3. Click "Start Run"
4. Look for `/api/run` request
5. Check:
   - **Status Code:** Should be 200
   - **Request Payload:** Should be JSON
   - **Response:** Should have `run_id`

### 3. Check Backend Logs

Watch the backend terminal for:
```
INFO:     127.0.0.1:xxxxx - "POST /run HTTP/1.1" 200 OK
[2024-xx-xx xx:xx:xx] [orchestrator] Received run request: ...
```

If you don't see these logs, the request isn't reaching the backend.

### 4. Check Frontend Logs

In browser console, you should see:
```
Starting run with PS: ...
Run started: {run_id: "...", status: "queued"}
```

---

## Environment Variables

### Backend (.env file)

```bash
# LLM Configuration
LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Paths
DATA_DIR=data
ARTIFACT_DIR=artifacts
DB_PATH=runs.db

# Optional: API Keys
KAGGLE_USERNAME=
KAGGLE_KEY=
HF_TOKEN=
```

### Frontend (.env file - if needed)

Create `automl-agent/frontend/.env`:
```bash
VITE_API_URL=/api
```

---

## Testing Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000 (or 5173)
- [ ] Can access http://localhost:8000/docs
- [ ] Can access http://localhost:3000 (or 5173)
- [ ] Browser console shows no errors
- [ ] Backend terminal shows startup messages
- [ ] Can generate problem statements
- [ ] Can select a problem statement
- [ ] Can click "Start Run" button
- [ ] Gets redirected to run details page
- [ ] Run details page shows "queued" or "running" status

---

## Still Having Issues?

### Collect Debug Information

1. **Backend logs** (copy from terminal)
2. **Frontend console errors** (F12 → Console → copy errors)
3. **Network request details** (F12 → Network → find /api/run → copy request/response)
4. **Environment info:**
   - Python version: `python --version`
   - Node version: `node --version`
   - npm version: `npm --version`
   - Operating System

### Reset Everything

If all else fails, try a complete reset:

```bash
# Stop both servers (Ctrl+C)

# Backend reset
cd automl-agent
del runs.db artifacts\*_log.txt    # Windows
rm runs.db artifacts/*_log.txt     # Mac/Linux
pip install -r requirements.txt --force-reinstall

# Frontend reset
cd frontend
rmdir /s /q node_modules           # Windows
rm -rf node_modules                # Mac/Linux
npm install

# Restart both servers
# Terminal 1: python start_server.py
# Terminal 2: cd frontend && npm run dev
```

---

## Quick Reference

### Backend Commands
```bash
cd automl-agent
venv\Scripts\activate              # Windows
source venv/bin/activate           # Mac/Linux
python start_server.py
```

### Frontend Commands
```bash
cd automl-agent/frontend
npm run dev
```

### Check Ports
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Mac/Linux
lsof -i :8000
lsof -i :3000
```

### View Logs
```bash
# Backend logs (in artifacts folder)
type artifacts\<run_id>_log.txt    # Windows
cat artifacts/<run_id>_log.txt     # Mac/Linux

# Database
sqlite3 runs.db "SELECT * FROM runs;"
```
