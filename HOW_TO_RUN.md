# How to Run the AutoML Platform

Complete step-by-step guide to run both backend and frontend.

---

## 📋 Prerequisites

Before starting, ensure you have:
- **Python 3.8+** installed
- **Node.js 16+** and **npm** installed
- **Git** (if cloning the repository)

---

## 🚀 Quick Start (Recommended)

### Option 1: Run Both Backend & Frontend Together

Open **TWO separate terminal windows** in the `automl-agent` directory.

#### Terminal 1 - Backend:
```bash
cd automl-agent

# Activate virtual environment (if you have one)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Run backend server
python start_server.py
```

Backend will start on: **http://localhost:8000**

#### Terminal 2 - Frontend:
```bash
cd automl-agent/frontend

# Install dependencies (first time only)
npm install

# Run frontend development server
npm run dev
```

Frontend will start on: **http://localhost:5173**

---

## 📝 Detailed Step-by-Step Instructions

### Step 1: Setup Backend

#### 1.1 Navigate to project directory
```bash
cd automl-agent
```

#### 1.2 Create virtual environment (first time only)
```bash
# Windows:
python -m venv venv

# Mac/Linux:
python3 -m venv venv
```

#### 1.3 Activate virtual environment
```bash
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

#### 1.4 Install Python dependencies (first time only)
```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (backend framework)
- FLAML (AutoML library)
- scikit-learn (ML library)
- pandas, numpy (data processing)
- And other required packages

#### 1.5 Configure environment variables
Check the `.env` file exists in `automl-agent/` directory:
```bash
# View .env file
type .env        # Windows
cat .env         # Mac/Linux
```

Key settings in `.env`:
```
LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

#### 1.6 Start the backend server
```bash
python start_server.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Backend is now running!** ✅

Keep this terminal open and running.

---

### Step 2: Setup Frontend

Open a **NEW terminal window** (keep backend running in the first one).

#### 2.1 Navigate to frontend directory
```bash
cd automl-agent/frontend
```

#### 2.2 Install Node.js dependencies (first time only)
```bash
npm install
```

This installs:
- React (UI framework)
- Vite (build tool)
- TailwindCSS (styling)
- React Router (navigation)
- And other frontend packages

#### 2.3 Start the frontend development server
```bash
npm run dev
```

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Frontend is now running!** ✅

---

## 🌐 Access the Application

1. Open your web browser
2. Go to: **http://localhost:5173**
3. You should see the AutoML Platform homepage

### Available Pages:
- **Home** (`/`) - Welcome page
- **New Run** (`/new`) - Start a new ML training run
- **All Runs** (`/runs`) - View all training runs
- **Run Details** (`/runs/:id`) - View specific run details

---

## 🧪 Test the Application

### Test 1: Create a New Run

1. Click **"Start New Run"** on homepage
2. Choose **"No - Suggest options"** for problem statement
3. Click **"Generate Problem Statement"**
4. Select one of the generated options
5. Click **"Start Training"**
6. You'll be redirected to the run details page
7. Watch the progress in real-time!

### Test 2: View Dataset Information

1. Wait for a run to complete
2. On the Run Details page, you should see:
   - **Dataset Information** card showing:
     - Source (e.g., "Kaggle", "Synthetic")
     - Dataset Name
     - Link to source (if available)
   - **Best Model** badge
   - **Model Performance** metrics
   - **Logs** showing execution details

---

## 🛑 Stopping the Application

### Stop Frontend:
In the frontend terminal, press: **Ctrl + C**

### Stop Backend:
In the backend terminal, press: **Ctrl + C**

---

## 🔄 Restarting the Application

You can restart anytime by running:

**Backend:**
```bash
cd automl-agent
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux
python start_server.py
```

**Frontend:**
```bash
cd automl-agent/frontend
npm run dev
```

---

## 📂 Project Structure

```
automl-agent/
├── app/                    # Backend code
│   ├── agents/            # ML agents (data, prep, automl, eval)
│   ├── utils/             # Utilities (LLM clients, logging)
│   └── main.py            # FastAPI application
├── frontend/              # Frontend code
│   ├── src/
│   │   ├── pages/        # React pages
│   │   ├── components/   # React components
│   │   └── services/     # API services
│   └── package.json
├── data/                  # Dataset storage
├── artifacts/             # Training artifacts
├── .env                   # Environment configuration
├── requirements.txt       # Python dependencies
└── start_server.py        # Backend startup script
```

---

## ⚙️ Configuration

### Backend Configuration (.env)

```bash
# LLM Settings
LLM_MODE=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Server Settings
HOST=0.0.0.0
PORT=8000

# Directories
DATA_DIR=data
ARTIFACT_DIR=artifacts
DB_PATH=runs.db
```

### Frontend Configuration

Frontend automatically connects to backend at `http://localhost:8000`

If you need to change this, edit:
```javascript
// frontend/src/services/api.js
const API_BASE_URL = 'http://localhost:8000'
```

---

## 🐛 Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

**Problem:** `Address already in use`
**Solution:** Port 8000 is busy. Kill the process or change port in `.env`

**Problem:** LLM errors
**Solution:** Make sure Ollama is running:
```bash
ollama serve
```

### Frontend Issues

**Problem:** `npm: command not found`
**Solution:** Install Node.js from https://nodejs.org/

**Problem:** `Cannot find module`
**Solution:** Install dependencies:
```bash
cd frontend
npm install
```

**Problem:** Port 5173 already in use
**Solution:** Vite will automatically try the next available port (5174, 5175, etc.)

### Connection Issues

**Problem:** Frontend can't connect to backend
**Solution:** 
1. Check backend is running on port 8000
2. Check browser console for errors
3. Verify `frontend/src/services/api.js` has correct URL

---

## 📊 Monitoring

### Backend Logs
Watch the backend terminal for:
- API requests
- Agent execution logs
- Error messages

### Frontend Logs
Open browser DevTools (F12) → Console tab to see:
- API calls
- React component logs
- JavaScript errors

### Database
View stored runs:
```bash
# In automl-agent directory
sqlite3 runs.db "SELECT run_id, status, created_at FROM runs;"
```

---

## 🎯 Next Steps

1. **Explore the UI** - Try different problem statements
2. **Upload your own dataset** - Use the dataset upload feature
3. **Check the logs** - Understand how the ML pipeline works
4. **View artifacts** - Download trained models and evaluation reports
5. **Customize** - Modify agents or UI to fit your needs

---

## 📞 Need Help?

- Check existing documentation in the `automl-agent/` directory
- Review logs in both terminals
- Check browser console for frontend errors
- Verify all dependencies are installed

---

## ✅ Success Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173
- [ ] Can access homepage in browser
- [ ] Can create a new run
- [ ] Can see dataset information in run details
- [ ] Can see best model and metrics
- [ ] Logs are updating in real-time

If all checked, you're ready to go! 🚀
