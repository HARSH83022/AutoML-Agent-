# Dataset Selection Logging Feature

## Overview

The system now displays **clear, formatted console output** showing which dataset is being used during the ML pipeline execution.

## What You'll See

### 1. Search Initialization
```
============================================================
🔍 SEARCHING FOR DATASETS
   Problem: Predict customer churn based on usage patterns...
   Task Type: classification
   Domain: business

   Search Order:
   1. User Upload
   2. Kaggle
   3. HuggingFace
   4. UCI ML Repository
   5. Synthetic (fallback)
============================================================
```

### 2. Dataset Selection (Kaggle Example)
```
============================================================
✅ DATASET SELECTED: Kaggle
   Dataset: username/customer-churn-dataset
   Rows: 10000
   Columns: 15
   Path: data/run123_kaggle_username_customer-churn-dataset.csv
============================================================
```

### 3. Dataset Selection (HuggingFace Example)
```
============================================================
✅ DATASET SELECTED: HuggingFace
   Dataset: scikit-learn/iris
   Rows: 150
   Columns: 5
   Path: data/run123_hf_scikit-learn_iris.csv
============================================================
```

### 4. Dataset Selection (UCI Example)
```
============================================================
✅ DATASET SELECTED: UCI ML Repository
   Dataset: iris
   Rows: 150
   Columns: 5
   Path: data/run123_uci_iris.csv
============================================================
```

### 5. Synthetic Fallback
```
============================================================
⚠️  FALLBACK: Generating Synthetic Dataset
   Reason: No suitable datasets found from external sources
============================================================

============================================================
✅ DATASET GENERATED: Synthetic
   Rows: 2000
   Columns: 6
   Path: data/run123_synthetic.csv
============================================================
```

### 6. User Upload
```
============================================================
✅ DATASET SELECTED: User Upload
   File: uploads/my_data.csv
   Rows: 5000
   Columns: 20
============================================================
```

## Benefits

1. **Transparency**: Users can see exactly which dataset is being used
2. **Debugging**: Easy to identify if wrong dataset was selected
3. **Traceability**: Clear audit trail of data sources
4. **User Confidence**: Builds trust by showing the system's decision-making

## Configuration

No configuration needed! The logging is automatic and works for all data sources.

## Example Output in Full Pipeline

```bash
$ python -m uvicorn app.main:app --reload

============================================================
🔍 SEARCHING FOR DATASETS
   Problem: Predict house prices...
   Task Type: regression
   Domain: real estate

   Search Order:
   1. User Upload
   2. Kaggle
   3. HuggingFace
   4. UCI ML Repository
   5. Synthetic (fallback)
============================================================

[Searching Kaggle...]
[Searching HuggingFace...]

============================================================
✅ DATASET SELECTED: Kaggle
   Dataset: harlfoxem/housesalesprediction
   Rows: 21613
   Columns: 21
   Path: data/abc123_kaggle_harlfoxem_housesalesprediction.csv
============================================================

[Preprocessing...]
[Training models...]
[Evaluating...]

✅ Pipeline completed successfully!
```

## Technical Details

- **Location**: `app/agents/data_agent.py`
- **Function**: `get_or_find_dataset()`
- **Output**: Both console (stdout) and log files
- **Format**: Boxed text with emojis for visual clarity

## Troubleshooting

If you don't see the output:
1. Check that you're running the server in the terminal (not background)
2. Ensure stdout is not redirected
3. Check log files in `artifacts/` directory for full details

