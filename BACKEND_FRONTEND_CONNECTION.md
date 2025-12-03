# 🔗 Backend-Frontend Connection Explained

## 📋 **Overview**

Your AutoML platform has a **React frontend** and a **FastAPI backend** that communicate via REST API.

---

## 🏗️ **Architecture**

```
┌─────────────────┐         HTTP/REST API        ┌──────────────────┐
│                 │  ────────────────────────────▶│                  │
│  React Frontend │                               │  FastAPI Backend │
│  (Port 3000)    │  ◀────────────────────────────│  (Port 8000)     │
│                 │         JSON Responses        │                  │
└─────────────────┘                               └──────────────────┘
```

---

## 🔌 **How They Connect**

### **1. API Base URL Configuration**

**Frontend** (`frontend/src/services/api.js`):
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
```

This means:
- **Development**: Uses environment variable `VITE_API_URL`
- **Production**: Falls back to `/api` (relative path)

### **2. API Client Setup**

**Frontend** creates an Axios client:
```javascript
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})
```

### **3. API Endpoints**

**Backend** (`app/main.py`) exposes these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/run` | POST | Start new ML run |
| `/status/{run_id}` | GET | Get run status |
| `/runs` | GET | List all runs |
| `/ps` | POST | Parse/generate problem statement |
| `/health` | GET | Health check |

**Frontend** (`frontend/src/services/api.js`) calls them:

```javascript
export const mlApi = {
  startRun: async (problemStatement, preferences) => {
    const response = await api.post('/run', payload)
    return response.data
  },
  
  getRunStatus: async (runId) => {
    const response = await api.get(`/status/${runId}`)
    return response.data
  },
  
  listRuns: async () => {
    const response = await api.get('/runs')
    return response.data
  },
  
  parseProblemStatement: async (text, hint) => {
    const response = await api.post('/ps', payload)
    return response.data
  }
}
```

---

## 🔄 **Request/Response Flow**

### **Example: Starting a New ML Run**

1. **User Action**: Clicks "Start Run" button in React frontend

2. **Frontend** (`NewRunPage.jsx`):
   ```javascript
   const response = await mlApi.startRun(
     formData.problemStatement,
     preferences
   )
   ```

3. **API Call** (`api.js`):
   ```javascript
   POST http://localhost:8000/run
   Body: {
     "problem_statement": "Predict iris species",
     "preferences": {
       "training_budget_minutes": 10,
       "primary_metric": "f1"
     }
   }
   ```

4. **Backend** (`app/main.py`):
   ```python
   @app.post("/run")
   def kick_off_run(req: RunRequest):
       run_id = str(uuid.uuid4())
       write_run_db(run_id, "queued", {"payload": req.dict()})
       return {"run_id": run_id, "status": "queued"}
   ```

5. **Response**:
   ```json
   {
     "run_id": "abc-123-def",
     "status": "queued"
   }
   ```

6. **Frontend**: Navigates to run details page and polls for updates

---

## 🌐 **Deployment Configurations**

### **Local Development**

**Backend**:
```bash
cd automl-agent
python start_server.py
# Runs on: http://localhost:8000
```

**Frontend**:
```bash
cd automl-agent/frontend
npm run dev
# Runs on: http://localhost:3000
```

**Frontend `.env`**:
```
VITE_API_URL=http://localhost:8000
```

---

### **Production Deployment**

#### **Option 1: Separate Deployments**

**Backend on Render**:
- URL: `https://automl-platform.onrender.com`
- Serves API endpoints

**Frontend on Vercel/Netlify**:
- URL: `https://automl-platform.vercel.app`
- Serves React app

**Frontend `.env.production`**:
```
VITE_API_URL=https://automl-platform.onrender.com
```

#### **Option 2: Single Deployment (Backend serves Frontend)**

**Backend** serves both API and static frontend:

```python
# app/main.py
from fastapi.staticfiles import StaticFiles

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

**Build process**:
```bash
# Build frontend
cd frontend
npm run build

# Deploy backend (includes frontend/dist)
cd ..
# Deploy to Render/Azure
```

**Frontend `.env.production`**:
```
VITE_API_URL=/api
```

---

## 🔒 **CORS Configuration**

For the frontend to call the backend from a different origin, CORS must be enabled.

**Backend** (`app/main.py`) - **NEEDS TO BE ADDED**:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoML Orchestrator")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**For development** (allow all origins):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📦 **Data Flow Example**

### **Creating a New ML Run**

```
User fills form → Frontend validates → API call to /run
                                            ↓
                                    Backend creates run_id
                                            ↓
                                    Queues run in database
                                            ↓
                                    Returns run_id to frontend
                                            ↓
                                    Frontend navigates to /runs/{run_id}
                                            ↓
                                    Frontend polls /status/{run_id} every 3s
                                            ↓
                                    Backend processes run (data → train → eval)
                                            ↓
                                    Frontend displays progress and results
```

---

## 🛠️ **Environment Variables**

### **Frontend** (`.env` or `.env.production`)

```bash
# API endpoint
VITE_API_URL=http://localhost:8000

# Or for production
VITE_API_URL=https://automl-platform.onrender.com
```

### **Backend** (`.env`)

```bash
# App settings
APP_ENV=production
LOG_LEVEL=info

# Kaggle credentials
KAGGLE_USERNAME=harsh83022
KAGGLE_KEY=04bd6ce5bcb813d98f2a83457af5c44a

# LLM settings
LLM_MODE=none
```

---

## 🚀 **Deployment Options**

### **Option 1: Backend + Frontend on Render**

1. **Deploy backend** as Web Service
2. **Build frontend** and include in backend
3. **Backend serves** both API and static files

**Pros**: Single deployment, simpler
**Cons**: Frontend changes require backend redeploy

### **Option 2: Backend on Render, Frontend on Vercel**

1. **Deploy backend** to Render
2. **Deploy frontend** to Vercel
3. **Configure** VITE_API_URL to point to Render

**Pros**: Independent deployments, faster frontend updates
**Cons**: Need to manage CORS, two deployments

### **Option 3: Both on Azure**

1. **Deploy backend** as Azure App Service
2. **Deploy frontend** as Azure Static Web App
3. **Configure** API URL

**Pros**: All in one cloud, good integration
**Cons**: More expensive, quota issues (as you experienced)

---

## 🔍 **Current Status**

Your project currently:
- ✅ Has backend API endpoints defined
- ✅ Has frontend API client configured
- ✅ Has proper request/response structure
- ❌ **Missing CORS configuration** (needs to be added)
- ❌ **Not deployed yet** (Azure had quota issues)

---

## ✅ **Next Steps for Deployment**

### **1. Add CORS to Backend**

Add this to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AutoML Orchestrator")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **2. Deploy Backend to Render**

- Push code to GitHub
- Connect to Render
- Use `render.yaml` configuration
- Get backend URL: `https://automl-platform.onrender.com`

### **3. Configure Frontend**

Create `frontend/.env.production`:
```
VITE_API_URL=https://automl-platform.onrender.com
```

### **4. Deploy Frontend**

**Option A: Include in backend**
```bash
cd frontend
npm run build
# Backend will serve frontend/dist
```

**Option B: Deploy to Vercel**
```bash
cd frontend
vercel deploy
```

---

## 📊 **Summary**

**Connection Method**: REST API over HTTP
**Protocol**: JSON
**Frontend**: React (Vite) on port 3000
**Backend**: FastAPI (Python) on port 8000
**API Client**: Axios
**Configuration**: Environment variables (VITE_API_URL)

**Key Files**:
- `frontend/src/services/api.js` - API client
- `app/main.py` - API endpoints
- `frontend/.env` - Frontend config
- `automl-agent/.env` - Backend config

Your backend and frontend are well-structured and ready to deploy! Just need to add CORS and deploy to Render. 🚀
