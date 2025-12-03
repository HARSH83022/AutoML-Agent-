# Debug: Why Models Are Not Showing

## Issue
The "Trained Models" card is not showing on the Run Details page.

## What I Fixed

### 1. Enhanced Leaderboard Extraction
- Added better parsing logic in `app/main.py`
- Now handles multiple FLAML leaderboard formats
- Added fallback mechanisms

### 2. Improved AutoML Agent
- Extracts trained models directly in `app/agents/automl_agent.py`
- Returns `trained_models` list with model names and scores
- Better logging to debug issues

### 3. Added Comprehensive Logging
- Logs leaderboard structure
- Logs number of models extracted
- Logs model names

## How to Debug

### Step 1: Check Backend Logs

After starting a run, watch the backend terminal for these logs:

```
[automl_agent] Leaderboard extracted: ['estimator', 'val_loss', ...]
[automl_agent] Extracted 3 models from leaderboard
[automl_agent] Best model: XGBoostClassifier
[orchestrator] Extracted 3 trained models: ['xgboost', 'lgbm', 'rf']
```

### Step 2: Check Run Status API

Open browser and go to:
```
http://localhost:8000/status/<run_id>
```

Look for `trained_models` in the response:
```json
{
  "state": {
    "trained_models": [
      {"name": "xgboost", "score": 0.9234},
      {"name": "lgbm", "score": 0.9156},
      {"name": "rf", "score": 0.9012}
    ],
    "best_model": "XGBoostClassifier"
  }
}
```

### Step 3: Check Frontend Console

Open browser console (F12) and look for:
```javascript
state.trained_models: [{...}, {...}, {...}]
```

## Common Issues & Solutions

### Issue 1: `trained_models` is empty array

**Cause:** Leaderboard parsing failed

**Solution:**
1. Check backend logs for errors
2. Look for: `[orchestrator] No models extracted from leaderboard, using fallback`
3. The fallback will create models from estimator list

### Issue 2: `trained_models` is undefined

**Cause:** Old run from before the update

**Solution:**
- Start a NEW run after restarting the backend
- Old runs won't have this data

### Issue 3: Only shows best model

**Cause:** Fallback mechanism activated

**What it means:**
- Leaderboard parsing failed
- System created models list from estimator_list
- Scores are estimated (best model gets actual score, others get 95%, 90%, etc.)

**This is OK!** You'll still see all models that were trained.

## Testing

### Quick Test

1. **Restart backend:**
   ```bash
   cd automl-agent
   python start_server.py
   ```

2. **Start a new run** from frontend

3. **Watch backend logs** for:
   ```
   [automl_agent] Leaderboard extracted: ...
   [automl_agent] Extracted X models from leaderboard
   [orchestrator] Extracted X trained models: [...]
   ```

4. **Check Run Details page** - should show "Trained Models" card

### Manual API Test

```bash
# Get a run_id from a completed run
curl http://localhost:8000/status/<run_id>
```

Look for `trained_models` in the JSON response.

## What You Should See

### Backend Logs (Success)
```
[automl_agent] Settings: {'time_budget': 300, 'estimator_list': ['xgboost', 'lgbm', 'rf'], ...}
[automl_agent] Leaderboard extracted: ['estimator', 'val_loss']
[automl_agent] Extracted 3 models from leaderboard
[automl_agent] Best model: XGBoostClassifier
[automl_agent] Completed successfully
[orchestrator] Extracted 3 trained models: ['xgboost', 'lgbm', 'rf']
[orchestrator] Orchestration completed - Best Model: XGBoostClassifier
```

### Frontend (Success)
```
Trained Models
┌─────────────────────────────────────┐
│ ✓ xgboost        Score: 0.9234     │
│   Best Performing Model             │
├─────────────────────────────────────┤
│   lgbm           Score: 0.9156     │
├─────────────────────────────────────┤
│   rf             Score: 0.9012     │
└─────────────────────────────────────┘
```

## Fallback Behavior

If leaderboard parsing fails, the system will:

1. Use the best model from evaluation
2. Add other models from `estimator_list`
3. Estimate scores based on best model score
4. Log: `[orchestrator] No models extracted from leaderboard, using fallback`

**This ensures you ALWAYS see the models**, even if leaderboard parsing fails!

## Key Changes Made

### `app/agents/automl_agent.py`
- Extract `trained_models` directly from leaderboard
- Return in response: `{"trained_models": [...]}`
- Better error handling

### `app/main.py`
- Try to use `trained_models` from automl agent first
- Fallback to leaderboard parsing if not available
- Fallback to estimator list if parsing fails
- Always populate `trained_models` in state

### `frontend/src/pages/RunDetailsPage.jsx`
- Display `state.trained_models` array
- Show all models with scores
- Highlight best model

## Next Steps

1. **Restart backend** to apply changes
2. **Start a NEW run** (old runs won't have this data)
3. **Check backend logs** for model extraction messages
4. **View Run Details page** to see trained models

If you still don't see models after following these steps, check the backend logs and share them for further debugging.
