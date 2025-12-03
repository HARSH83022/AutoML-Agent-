# Frontend-Backend Connection Fix

## Problem
After selecting a problem statement and clicking "Start Run", nothing happened. The run was not starting.

## Root Cause
The frontend was sending data in the wrong format:
- **Frontend was sending:** `FormData` with `multipart/form-data` headers
- **Backend was expecting:** JSON with `application/json` headers

## Solution Applied

### Fixed File: `frontend/src/services/api.js`

**Before (Wrong):**
```javascript
startRun: async (problemStatement, preferences = {}, uploadFile = null) => {
  const formData = new FormData()
  formData.append('problem_statement', problemStatement)
  formData.append('preferences', JSON.stringify(preferences))
  
  if (uploadFile) {
    formData.append('file', uploadFile)
  }
  
  const response = await api.post('/run', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}
```

**After (Correct):**
```javascript
startRun: async (problemStatement, preferences = {}, uploadFile = null) => {
  // Backend expects JSON format with RunRequest model
  const payload = {
    problem_statement: problemStatement,
    preferences: preferences,
    user: {}
  }
  
  // If file is provided, note it in user object
  if (uploadFile) {
    payload.user.upload_path = uploadFile.name
  }
  
  const response = await api.post('/run', payload)
  return response.data
}
```

## How to Apply the Fix

### Option 1: Automatic (Already Applied)
The fix has been automatically applied to your code. Just restart the frontend:

```bash
# Stop frontend (Ctrl+C)
cd automl-agent/frontend
npm run dev
```

### Option 2: Manual Verification
If you want to verify the fix was applied:

1. Open `automl-agent/frontend/src/services/api.js`
2. Find the `startRun` function
3. Verify it sends JSON payload (not FormData)

## Testing the Fix

1. **Start Backend:**
   ```bash
   cd automl-agent
   python start_server.py
   ```

2. **Start Frontend:**
   ```bash
   cd automl-agent/frontend
   npm run dev
   ```

3. **Test in Browser:**
   - Go to http://localhost:3000 (or 5173)
   - Click "Start New Run"
   - Choose "No - Generate suggestions"
   - Click "Generate Problem Statements"
   - Select one of the options
   - Click "Start Run"
   - **Expected:** You should be redirected to run details page
   - **Expected:** Run status should show "queued" then "running"

## What Changed

### Data Format
The backend expects this JSON structure:
```json
{
  "problem_statement": "Your problem statement here",
  "preferences": {
    "training_budget_minutes": 5,
    "primary_metric": "f1"
  },
  "user": {}
}
```

### Backend Endpoint
The `/run` endpoint in `app/main.py` uses Pydantic's `RunRequest` model:
```python
class RunRequest(BaseModel):
    run_id: Optional[str] = None
    user: Dict[str, Any] = {}
    mode: str = "ps_provided"
    problem_statement: Optional[str] = None
    preferences: Dict[str, Any] = {}
```

This model expects JSON, not FormData.

## Verification

### Check Browser Console (F12)
After clicking "Start Run", you should see:
```
POST /api/run 200 OK
```

### Check Backend Terminal
You should see:
```
INFO:     127.0.0.1:xxxxx - "POST /run HTTP/1.1" 200 OK
[timestamp] [orchestrator] Received run request: ...
```

### Check Network Tab (F12 → Network)
1. Find the `/api/run` request
2. **Request Headers:** Should show `Content-Type: application/json`
3. **Request Payload:** Should show JSON object
4. **Response:** Should show `{"run_id": "...", "status": "queued"}`

## Additional Notes

### File Upload
The current implementation doesn't fully support file uploads yet. If you select a file:
- The filename is passed to the backend in `user.upload_path`
- The backend will look for this file in the `data/` directory
- For full file upload support, additional backend changes would be needed

### API Proxy
The frontend uses Vite's proxy to forward `/api/*` requests to `http://localhost:8000`:
```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
    rewrite: (path) => path.replace(/^\/api/, '')
  }
}
```

This means:
- Frontend calls: `/api/run`
- Gets proxied to: `http://localhost:8000/run`

## Troubleshooting

If the fix doesn't work:

1. **Clear browser cache:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Check both servers are running**
3. **Check browser console for errors**
4. **Check backend terminal for errors**
5. **See TROUBLESHOOTING.md for detailed debugging steps**

## Success Indicators

✅ Click "Start Run" button
✅ No errors in browser console
✅ Redirected to `/runs/:id` page
✅ Run status shows "queued" or "running"
✅ Backend terminal shows "Received run request"
✅ Logs start appearing in run details page

If all these are true, the connection is working! 🎉
