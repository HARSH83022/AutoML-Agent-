# Dataset Source Display Feature

## Overview
Enhanced the AutoML platform to display dataset source information in the UI, showing users which dataset is being used and where it came from.

## Changes Made

### 1. Backend - Data Agent (`app/agents/data_agent.py`)
**Modified**: `get_or_find_dataset()` function

**Changes**:
- Changed return type from `str` (just path) to `Dict` containing:
  - `dataset_path`: Path to the CSV file
  - `source`: Source platform (e.g., "Kaggle", "HuggingFace", "User Upload", "UCI ML Repository", "Synthetic")
  - `source_name`: Name/identifier of the dataset
  - `source_url`: URL to the dataset source (when available)

**Updated for all data sources**:
- ✅ User Upload
- ✅ Kaggle
- ✅ HuggingFace
- ✅ UCI ML Repository
- ✅ Synthetic Generation

### 2. Backend - Orchestrator (`app/main.py`)
**Modified**: `orchestrate_run()` function

**Changes**:
- Extract dataset metadata from data agent response
- Store dataset source information in run state:
  - `dataset_source`
  - `dataset_source_name`
  - `dataset_source_url`
- Pass this information through to completion state for frontend access

### 3. Frontend - Run Details Page (`frontend/src/pages/RunDetailsPage.jsx`)
**Added**: New "Dataset Information" card

**Features**:
- Displays dataset source (e.g., "Kaggle", "HuggingFace")
- Shows dataset name/identifier
- Provides clickable link to original dataset source (when URL available)
- Beautiful gradient design with blue/indigo theme
- Positioned above the Model Performance section

## UI Design
The dataset information is displayed in an attractive card with:
- Gradient background (blue-50 to indigo-50)
- Two-column grid layout showing Source and Dataset Name
- Optional external link to view the original dataset
- Consistent styling with the rest of the application

## Example Display
```
Dataset Information
┌─────────────────────────────────────────┐
│ Source: Kaggle                          │
│ Dataset Name: username/dataset-name     │
│ [View Dataset Source →]                 │
└─────────────────────────────────────────┘
```

## Benefits
1. **Transparency**: Users can see exactly which dataset is being used
2. **Traceability**: Easy to track data sources for compliance/auditing
3. **Reproducibility**: Users can access the original dataset if needed
4. **Trust**: Builds confidence by showing data provenance

## Testing
To test this feature:
1. Start a new ML run from the frontend
2. Navigate to the run details page
3. Observe the "Dataset Information" card showing:
   - Source platform
   - Dataset name
   - Link to original source (if available)

## Backward Compatibility
The changes are backward compatible:
- If data agent returns old format (string), orchestrator handles it gracefully
- Frontend only displays dataset info when available in state
- No breaking changes to existing functionality
