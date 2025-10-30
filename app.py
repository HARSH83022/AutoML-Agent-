# from fastapi import FastAPI, HTTPException, UploadFile, File
# from pydantic import BaseModel
# from typing import List, Dict
# import pandas as pd
# import io
# import os
# from preprocessing_agent import preprocess  # your fully refactored preprocessing function
# from typing import List, Dict, Optional, Any


# app = FastAPI(title="Dynamic Preprocessing Agent API")

# # ------------------------
# # Root Endpoint
# # ------------------------
# @app.get("/")
# def root():
#     return {"message": "🚀 Preprocessing Agent API is running!"}

# # ------------------------
# # JSON Input Endpoint
# # ------------------------
# class DataItem(BaseModel):
#     features: Dict[str, Any]

# class PreprocessingRequest(BaseModel):
#     data: List[DataItem]

# @app.post("/run_preprocessing/json")
# def run_preprocessing_json(request: PreprocessingRequest, save_csv: bool = False):
#     """
#     Preprocess JSON input data.
#     - `save_csv`: if True, saves the processed data as CSV in ./outputs
#     """
#     data_list = [item.features for item in request.data]
    
#     try:
#         result = preprocess(data_list)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")
    
#     # Optionally save processed CSV
#     if save_csv:
#         os.makedirs("./outputs", exist_ok=True)
#         pd.DataFrame(result["processed_data"]).to_csv("./outputs/processed_json.csv", index=False)
#         result["processed_csv"] = "./outputs/processed_json.csv"

#     return result

# # ------------------------
# # CSV Input Endpoint
# # ------------------------
# @app.post("/run_preprocessing/csv")
# async def run_preprocessing_csv(file: UploadFile = File(...), save_csv: bool = False):
#     """
#     Preprocess CSV file upload.
#     - `save_csv`: if True, saves the processed data as CSV in ./outputs
#     """
#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
#     try:
#         contents = await file.read()
#         df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
#         data_list = df.to_dict(orient="records")
#         result = preprocess(data_list)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    
#     # Optionally save processed CSV
#     if save_csv:
#         os.makedirs("./outputs", exist_ok=True)
#         pd.DataFrame(result["processed_data"]).to_csv("./outputs/processed_csv.csv", index=False)
#         result["processed_csv"] = "./outputs/processed_csv.csv"

#     return result


from fastapi import BackgroundTasks, HTTPException, Query
from typing import Optional
import pandas as pd
import requests

@app.post("/run_preprocessing/json")
def run_preprocessing_json(
    request: PreprocessingRequest,
    background_tasks: BackgroundTasks,
    save_csv: Optional[bool] = Query(True)
):
    if preprocess is None:
        raise HTTPException(status_code=500, detail="❌ Preprocessing module not found")

    save_csv = bool(str(save_csv).lower() == "true")

    try:
        # Convert incoming data to DataFrame
        df = pd.DataFrame([item.features for item in request.data])
        df = df.where(pd.notnull(df), None)

        # Run preprocessing
        result = preprocess(df, save_artifacts=save_csv)

        # Safely extract processed file path (handles both formats)
        processed_uri = (
            result.get("result", {}).get("artifacts", {}).get("processed_uri") or
            result.get("artifacts", {}).get("processed_uri") or
            result.get("processed_uri")
        )

        if not processed_uri:
            raise ValueError("❌ Processed URI not found in preprocessing output")

        # Prepare payload for Model Selection Agent
        model_selection_payload = {
            "processed_csv_path": processed_uri,
            "target_column": "category_A"  # ⚠️ Change this to your real target column
        }

        # Trigger Model Selection Agent automatically
        background_tasks.add_task(
            requests.post,
            "http://127.0.0.1:8000/model_selection",
            json=model_selection_payload
        )

        return {
            "status": "✅ Preprocessing successful & Model Selection triggered",
            "processed_uri": processed_uri,
            "raw_result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")

@app.post("/run_preprocessing/csv")
async def run_preprocessing_csv(file: UploadFile = File(...), save_csv: Optional[bool] = Query(True)):
    if preprocess is None:
        raise HTTPException(status_code=500, detail="❌ Preprocessing module not found")

    save_csv = bool(str(save_csv).lower() == "true")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        result = preprocess(df, save_artifacts=save_csv)
        return {"status": "✅ CSV preprocessing successful", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")

@app.post("/run_preprocessing/excel")
async def run_preprocessing_excel(file: UploadFile = File(...), save_csv: Optional[bool] = Query(True)):
    if preprocess is None:
        raise HTTPException(status_code=500, detail="❌ Preprocessing module not found")

    save_csv = bool(str(save_csv).lower() == "true")

    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are supported")

    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        result = preprocess(df, save_artifacts=save_csv)
        return {"status": "✅ Excel preprocessing successful", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Excel: {str(e)}")

# -----------------------------
# Model Selection Endpoint
# -----------------------------
# @app.post("/model_selection")
# def run_model_selection(data: Dict[str, Any] = Body(...)):
#     if model_selection is None:
#         raise HTTPException(status_code=500, detail="❌ Model Selection module not found")
#     try:
#         result = model_selection(data)
#         return {"status": "✅ Model selection completed", "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in model selection: {str(e)}")
# -----------------------------
@app.post("/model_selection")
def run_model_selection(data: Dict[str, Any] = Body(...)):
    if model_selection is None:
        raise HTTPException(status_code=500, detail="❌ Model Selection module not found")

    try:
        # Extract inputs
        processed_csv_path = data.get("processed_csv_path")
        target_column = data.get("target_column")

        if not processed_csv_path or not os.path.exists(processed_csv_path):
            raise ValueError(f"Processed CSV not found: {processed_csv_path}")
        if not target_column:
            raise ValueError("Target column not provided")

        # Load preprocessed data
        df = pd.read_csv(processed_csv_path)
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")

        # Call the model selection agent logic
        result = model_selection(df, target_column)

        return {
            "status": "✅ Model selection completed successfully",
            "result": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in model selection: {str(e)}")

# Model Training Endpoint
# -----------------------------
@app.post("/model_training")
async def model_training(payload: dict):
    try:
        processed_csv_path = payload.get("processed_csv_path")
        target_column = payload.get("target_column")
        model_name = payload.get("model_name", "auto")

        if not processed_csv_path or not target_column:
            return {"error": "processed_csv_path and target_column are required"}

        df = pd.read_csv(processed_csv_path)

        result = train_model_agent(
            df=df,
            target=target_column,
            model_type=model_name
        )

        return {"status": "✅ Model Training Completed", "result": result}

    except Exception as e:
        return {"detail": f"Error in model training: {e}"}

# -----------------------------
# Evaluation Endpoint
# -----------------------------
@app.post("/evaluation")
def run_evaluation(data: Dict[str, Any] = Body(...)):
    if evaluate_model is None:
        raise HTTPException(status_code=500, detail="❌ Evaluation module not found")
    try:
        model = data.get("model")
        X_test = pd.DataFrame(data["X_test"]) if isinstance(data["X_test"], list) else data["X_test"]
        y_test = data.get("y_test")

        result = evaluate_model(model, X_test, y_test)
        return {"status": "✅ Evaluation completed", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in evaluation: {str(e)}")

# -----------------------------
# Report Generation Endpoint
# -----------------------------
@app.post("/report_generation")
def run_report_generation(data: Dict[str, Any] = Body(...)):
    if generate_report is None:
        raise HTTPException(status_code=500, detail="❌ Report Generation module not found")
    try:
        path = data.get("save_path", "./outputs/training_report.html")
        preproc_summary = data.get("preproc_summary", {})
        training_summary = data.get("training_summary", {})
        evaluation_summary = data.get("evaluation_summary", {})

        report_path = generate_report(
            preproc_summary=preproc_summary,
            training_summary=training_summary,
            evaluation_summary=evaluation_summary,
            save_path=path
        )
        return {"status": "✅ Report generated", "report_path": report_path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in report generation: {str(e)}")
