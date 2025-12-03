# 🚀 How to Run the Frontend

## Prerequisites

Make sure you have **Node.js** installed (version 16 or higher):
```bash
node --version
npm --version
```

If not installed, download from: https://nodejs.org/

---

## Step-by-Step Instructions

### 1️⃣ Navigate to Frontend Directory

```bash
cd automl-agent/frontend
```

### 2️⃣ Install Dependencies (First Time Only)

```bash
npm install
```

This will install all required packages (React, Vite, TailwindCSS, etc.)

**Expected output:**
```
added 234 packages in 15s
```

### 3️⃣ Start the Development Server

```bash
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### 4️⃣ Open in Browser

Open your browser and go to:
```
http://localhost:3000
```

---

## ✅ What You Should See

1. **Homepage** with:
   - "AutoML No-Code Platform" title
   - "Start New Run" button
   - Recent runs list

2. **Navigation**:
   - Click "Start New Run" → Form to create ML run
   - Enter problem statement → Click "Start Run"
   - Redirects to Run Details page with real-time updates

---

## 🔧 Troubleshooting

### Problem: `npm: command not found`
**Solution:** Install Node.js from https://nodejs.org/

### Problem: Port 3000 already in use
**Solution:** Kill the process or use a different port:
```bash
npm run dev -- --port 3001
```

### Problem: Dependencies not installing
**Solution:** Clear npm cache and retry:
```bash
npm cache clean --force
npm install
```

### Problem: Frontend can't connect to backend
**Solution:** Make sure backend is running on port 8000:
```bash
# In another terminal, from automl-agent directory:
uvicorn app.main:app --reload --port 8000
```

---

## 🎯 Complete Setup (Backend + Frontend)

### Terminal 1 - Backend:
```bash
cd automl-agent
python -m venv venv
venv\Scripts\activate          # Windows
# OR
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2 - Frontend:
```bash
cd automl-agent/frontend
npm install
npm run dev
```

### Access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Dashboard**: http://localhost:8000/dashboard

---

## 📦 Production Build

To build for production:

```bash
cd automl-agent/frontend
npm run build
```

Output will be in `dist/` directory.

To preview production build:
```bash
npm run preview
```

---

## 🎨 Development Tips

### Hot Reload
Changes to React files automatically reload in the browser.

### API Proxy
The frontend proxies `/api/*` requests to `http://localhost:8000/*` automatically.

### Environment Variables
Create `automl-agent/frontend/.env` file:
```
VITE_API_URL=/api
```

### Code Formatting
```bash
npm run format
npm run lint
```

---

## 📱 Features Available

✅ **Start New Run**
- Enter problem statement
- Set training budget
- Choose primary metric
- Upload dataset (optional)

✅ **View Run Details**
- Real-time status updates (every 2 seconds)
- Live logs
- Current phase (PS parsing → Data search → Preprocessing → Training → Evaluation)
- Download artifacts

✅ **View All Runs**
- List of all ML runs
- Filter by status
- Quick access to details

✅ **Responsive Design**
- Works on desktop, tablet, and mobile

---

## 🆘 Need Help?

1. Check backend is running: http://localhost:8000/docs
2. Check frontend console for errors (F12 in browser)
3. Check backend logs in terminal
4. Verify `.env` file has correct API keys

---

## 🎉 You're Ready!

Once both backend and frontend are running:

1. Go to http://localhost:3000
2. Click "Start New Run"
3. Enter: "Predict customer churn"
4. Click "Start Run"
5. Watch the magic happen! 🚀

The system will:
- Parse your problem
- Find a dataset from Kaggle/HuggingFace
- Clean and preprocess data
- Train 5-10 ML models
- Evaluate and show results
- Generate visualizations
- Provide downloadable artifacts

**Everything is fully automated!** ✨
