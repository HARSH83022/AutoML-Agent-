# Frontend-Backend Integration Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    User Browser                          │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         React Frontend (Port 3000)              │    │
│  │  - Vite Dev Server                              │    │
│  │  - React Router                                 │    │
│  │  - Axios API Client                             │    │
│  │  - TailwindCSS                                  │    │
│  └────────────┬───────────────────────────────────┘    │
│               │ HTTP Requests                           │
│               │ /api/* → Proxy                          │
└───────────────┼─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)                      │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  REST API Endpoints                             │    │
│  │  - POST /run                                    │    │
│  │  - GET /status/{run_id}                         │    │
│  │  - GET /runs                                    │    │
│  │  - POST /ps                                     │    │
│  │  - GET /artifacts/{file}                        │    │
│  └────────────┬───────────────────────────────────┘    │
│               │                                          │
│  ┌────────────▼───────────────────────────────────┐    │
│  │  7 Specialized Agents                           │    │
│  │  - PS Agent                                     │    │
│  │  - Data Agent (Kaggle/HF/UCI)                   │    │
│  │  - Prep Agent                                   │    │
│  │  - AutoML Agent (FLAML)                         │    │
│  │  - Eval Agent                                   │    │
│  │  - Deploy Agent                                 │    │
│  │  - Synthetic Data Agent                         │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## API Integration

### Frontend API Service (`src/services/api.js`)

```javascript
import axios from 'axios'

const API_BASE_URL = '/api'  // Proxied to http://localhost:8000

export const mlApi = {
  startRun: async (problemStatement, preferences, file) => {
    const formData = new FormData()
    formData.append('problem_statement', problemStatement)
    formData.append('preferences', JSON.stringify(preferences))
    if (file) formData.append('file', file)
    
    const response = await axios.post(`${API_BASE_URL}/run`, formData)
    return response.data
  },
  
  getRunStatus: async (runId) => {
    const response = await axios.get(`${API_BASE_URL}/status/${runId}`)
    return response.data
  },
  
  listRuns: async () => {
    const response = await axios.get(`${API_BASE_URL}/runs`)
    return response.data
  }
}
```

### Backend API Endpoints (`app/main.py`)

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def start_run(
    problem_statement: str,
    preferences: dict = {},
    file: UploadFile = File(None)
):
    # Start ML pipeline
    run_id = orchestrate_run(problem_statement, preferences, file)
    return {"run_id": run_id, "status": "started"}

@app.get("/status/{run_id}")
async def get_status(run_id: str):
    # Get run status
    status = get_run_status(run_id)
    return status
```

---

## Development Workflow

### 1. Local Development (Separate Servers)

**Terminal 1 - Backend:**
```bash
cd automl-agent
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd automl-agent/frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 2. Docker Development (Integrated)

```bash
docker-compose up
```

**Access:**
- Application: http://localhost:8000
- Frontend served from `/static`
- API at `/api/*`

---

## Proxy Configuration

### Vite Proxy (Development)

`frontend/vite.config.js`:
```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

**How it works:**
- Frontend request: `GET /api/runs`
- Proxied to: `GET http://localhost:8000/runs`
- No CORS issues in development

### Nginx Proxy (Production)

`nginx.conf`:
```nginx
server {
    listen 80;
    
    # Frontend
    location / {
        root /app/static;
        try_files $uri /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://automl-platform:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Data Flow Examples

### Example 1: Starting a New Run

**Frontend (NewRunPage.jsx):**
```javascript
const handleSubmit = async (e) => {
  e.preventDefault()
  
  const response = await mlApi.startRun(
    formData.problemStatement,
    { training_budget_minutes: 5 },
    formData.file
  )
  
  navigate(`/runs/${response.run_id}`)
}
```

**Backend (main.py):**
```python
@app.post("/run")
async def start_run(problem_statement: str, ...):
    run_id = str(uuid.uuid4())
    
    # Start background task
    background_tasks.add_task(
        orchestrate_run,
        run_id,
        problem_statement,
        preferences
    )
    
    return {"run_id": run_id}
```

**Flow:**
1. User fills form → clicks "Start Run"
2. Frontend sends POST to `/api/run`
3. Backend creates run_id, starts background task
4. Frontend redirects to `/runs/{run_id}`
5. Frontend polls `/api/status/{run_id}` for updates

### Example 2: Real-time Status Updates

**Frontend (RunDetailsPage.jsx):**
```javascript
useEffect(() => {
  const interval = setInterval(async () => {
    const status = await mlApi.getRunStatus(runId)
    setRunData(status)
    
    if (status.status === 'completed' || status.status === 'failed') {
      clearInterval(interval)
    }
  }, 2000)  // Poll every 2 seconds
  
  return () => clearInterval(interval)
}, [runId])
```

**Backend (main.py):**
```python
@app.get("/status/{run_id}")
async def get_status(run_id: str):
    run = get_run_from_db(run_id)
    
    return {
        "run_id": run_id,
        "status": run.status,  # running, completed, failed
        "phase": run.current_phase,  # data, prep, train, eval
        "progress": run.progress_pct,
        "logs": run.recent_logs,
        "results": run.results if run.status == "completed" else None
    }
```

---

## State Management

### Frontend State

```javascript
// Run status states
const [runData, setRunData] = useState({
  run_id: null,
  status: 'pending',  // pending, running, completed, failed
  phase: null,        // data, prep, train, eval, deploy
  progress: 0,
  logs: [],
  results: null
})
```

### Backend State

```python
# SQLite database
class Run:
    run_id: str
    status: str  # pending, running, completed, failed
    phase: str   # data, prep, train, eval, deploy
    progress: int
    created_at: datetime
    completed_at: datetime
    results: dict
```

---

## Error Handling

### Frontend Error Handling

```javascript
try {
  const response = await mlApi.startRun(...)
  navigate(`/runs/${response.run_id}`)
} catch (error) {
  if (error.response) {
    // Backend returned error
    alert(`Error: ${error.response.data.detail}`)
  } else if (error.request) {
    // Network error
    alert('Cannot connect to server')
  } else {
    // Other error
    alert('An error occurred')
  }
}
```

### Backend Error Handling

```python
from fastapi import HTTPException

@app.post("/run")
async def start_run(...):
    try:
        run_id = orchestrate_run(...)
        return {"run_id": run_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## File Upload Handling

### Frontend

```javascript
const [file, setFile] = useState(null)

<input
  type="file"
  accept=".csv"
  onChange={(e) => setFile(e.target.files[0])}
/>

// Send file
await mlApi.startRun(problemStatement, preferences, file)
```

### Backend

```python
from fastapi import UploadFile, File

@app.post("/run")
async def start_run(
    problem_statement: str,
    file: UploadFile = File(None)
):
    if file:
        # Save uploaded file
        file_path = f"data/{run_id}_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())
```

---

## WebSocket Support (Optional Enhancement)

For real-time updates instead of polling:

### Backend

```python
from fastapi import WebSocket

@app.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    
    while True:
        status = get_run_status(run_id)
        await websocket.send_json(status)
        
        if status["status"] in ["completed", "failed"]:
            break
        
        await asyncio.sleep(1)
```

### Frontend

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/${runId}`)

ws.onmessage = (event) => {
  const status = JSON.parse(event.data)
  setRunData(status)
}
```

---

## Testing Integration

### Frontend Tests

```javascript
// src/services/api.test.js
import { mlApi } from './api'

test('startRun returns run_id', async () => {
  const response = await mlApi.startRun('Test problem', {})
  expect(response).toHaveProperty('run_id')
})
```

### Backend Tests

```python
# tests/test_api.py
def test_start_run(client):
    response = client.post("/run", json={
        "problem_statement": "Test problem"
    })
    assert response.status_code == 200
    assert "run_id" in response.json()
```

---

## Production Build

### Build Frontend

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

### Serve from Backend

```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
```

### Docker Build

```dockerfile
# Build frontend
FROM node:18 AS frontend-builder
COPY frontend/ ./
RUN npm ci && npm run build

# Copy to backend
FROM python:3.10
COPY --from=frontend-builder /app/dist ./app/static
```

---

## Monitoring

### Frontend Monitoring

```javascript
// Track API calls
axios.interceptors.request.use(config => {
  console.log(`API Call: ${config.method} ${config.url}`)
  return config
})
```

### Backend Monitoring

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    return response
```

---

## Summary

✅ **Frontend**: React + Vite + TailwindCSS
✅ **Backend**: FastAPI + Python
✅ **Integration**: Axios + Proxy
✅ **Development**: Separate servers with proxy
✅ **Production**: Single Docker container
✅ **CI/CD**: GitHub Actions pipeline
✅ **Deployment**: Docker + Cloud platforms

The frontend and backend are fully integrated and production-ready! 🚀
