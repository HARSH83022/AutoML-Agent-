


# from fastapi import FastAPI, HTTPException, UploadFile, File, Form
# from pydantic import BaseModel
# from typing import List, Dict, Optional, Any
# import pandas as pd
# import io
# import os
# import joblib

# # Import your preprocessing function
# from preprocessing_agent import preprocess

# app = FastAPI(title="Dynamic Preprocessing Agent API")

# # ================================
# # Root endpoint
# # ================================
# @app.get("/")
# def root():
#     return {"message": "🚀 Preprocessing Agent API is running!"}

# # ================================
# # JSON Input Endpoint
# # ================================
# class DataItem(BaseModel):
#     features: Dict[str, Any]

# class PreprocessingRequest(BaseModel):
#     data: List[DataItem]

# @app.post("/run_preprocessing/json")
# def run_preprocessing_json(
#     request: PreprocessingRequest,
#     target: Optional[str] = Form(None),
#     split: Optional[bool] = Form(False),
#     imbalance: Optional[bool] = Form(False),
#     save_csv: Optional[bool] = Form(True),
#     reuse_transformer: Optional[bool] = Form(False)
# ):
#     data_list = [item.features for item in request.data]
    
#     # Preprocess the data
#     try:
#         result = preprocess(
#             data=data_list,
#             target=target,
#             split=split,
#             imbalance=imbalance,
#             save_artifacts=save_csv
#         )
#         # If reuse_transformer is True, load previous transformer
#         if reuse_transformer and os.path.exists("./outputs/latest_transformer.joblib"):
#             transformer = joblib.load("./outputs/latest_transformer.joblib")
#             df = pd.DataFrame(data_list)
#             df_processed = transformer.transform(df)
#             result["processed_data"] = pd.DataFrame(
#                 df_processed, columns=transformer.get_feature_names_out()
#             ).to_dict(orient="records")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")
    
#     # Save transformer as latest for reuse
#     if save_csv:
#         os.makedirs("./outputs", exist_ok=True)
#         joblib.dump(result.get("artifacts", {}).get("transformer_uri"), "./outputs/latest_transformer.joblib")
    
#     return result

# # ================================
# # CSV File Upload Endpoint
# # ================================
# @app.post("/run_preprocessing/csv")
# async def run_preprocessing_csv(
#     file: UploadFile = File(...),
#     target: Optional[str] = Form(None),
#     split: Optional[bool] = Form(False),
#     imbalance: Optional[bool] = Form(False),
#     save_csv: Optional[bool] = Form(True),
#     reuse_transformer: Optional[bool] = Form(False)
# ):
#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
#     try:
#         contents = await file.read()
#         df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
#         # Reuse previous transformer if required
#         if reuse_transformer and os.path.exists("./outputs/latest_transformer.joblib"):
#             transformer = joblib.load("./outputs/latest_transformer.joblib")
#             df_processed = transformer.transform(df)
#             processed_data = pd.DataFrame(
#                 df_processed, columns=transformer.get_feature_names_out()
#             ).to_dict(orient="records")
#             result = {"processed_data": processed_data}
#         else:
#             # Preprocess normally
#             result = preprocess(
#                 data=df,
#                 target=target,
#                 split=split,
#                 imbalance=imbalance,
#                 save_artifacts=save_csv
#             )
#             # Save transformer as latest
#             if save_csv:
#                 os.makedirs("./outputs", exist_ok=True)
#                 joblib.dump(result.get("artifacts", {}).get("transformer_uri"), "./outputs/latest_transformer.joblib")
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    
#     return result





# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# import pandas as pd
# import io
# import os

# from preprocessing_agent import preprocess
# from training_agent import train_model_agent
# from evaluation_agent import evaluate_model
# from report_agent import generate_report
# import joblib

# app = FastAPI(title="Full ML Pipeline API")

# # -------------------------------
# # Preprocessing Endpoints
# # -------------------------------
# @app.post("/run_preprocessing/csv")
# async def preprocess_csv(file: UploadFile = File(...)):
#     contents = await file.read()
#     df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
#     result = preprocess(df)
#     # Save latest parquet
#     latest_path = "./outputs/latest_preprocessed.parquet"
#     pd.DataFrame(result["processed_data"]).to_parquet(latest_path)
#     return result

# # -------------------------------
# # Model Training Endpoint
# # -------------------------------
# @app.post("/train_model")
# def train_model(target: str = Form(...)):
#     latest_path = "./outputs/latest_preprocessed.parquet"
#     if not os.path.exists(latest_path):
#         raise HTTPException(status_code=400, detail="No preprocessed data found.")
#     df = pd.read_parquet(latest_path)
#     result = train_model_agent(df, target=target)
#     # Save trained model path
#     model_path = result["artifacts"]["model_uri"]
#     model = joblib.load(model_path)
#     result["evaluation"] = evaluate_model(model, df.drop(columns=[target]), df[target])
#     return result

# # -------------------------------
# # Generate Report Endpoint
# # -------------------------------
# @app.post("/generate_report")
# def report():
#     preproc_summary = {"info": "Preprocessing completed"}  # You can pass actual summary
#     training_summary = {"info": "Training completed"}      # Actual training metrics
#     evaluation_summary = {"info": "Evaluation metrics"}    # Actual evaluation metrics
#     path = generate_report(preproc_summary, training_summary, evaluation_summary)
#     return {"report_path": path}


# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.responses import JSONResponse
# import pandas as pd
# import uvicorn
# from typing import List, Dict
# import io
# from preprocessing_agent import preprocess

# app = FastAPI(title="Universal Preprocessing API", version="2.0")

# @app.get("/")
# def home():
#     return {"message": "✅ Welcome to the Universal Preprocessing Agent API"}

# # --------------------------- JSON Endpoint ---------------------------
# @app.post("/run_preprocessing/json")
# async def run_preprocessing_json(data: Dict):
#     """
#     Accepts JSON data and preprocesses it.
#     Example:
#     {
#       "data": [{"feature1": 10, "feature2": 20, "category": "A"}]
#     }
#     """
#     try:
#         if "data" not in data:
#             return JSONResponse(status_code=400, content={"error": "Missing 'data' field in JSON."})
        
#         result = preprocess(data["data"])
#         return JSONResponse(content=result)
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": f"Error in preprocessing JSON: {str(e)}"})

# # --------------------------- CSV Endpoint ---------------------------
# @app.post("/run_preprocessing/csv")
# async def run_preprocessing_csv(
#     file: UploadFile = File(...),
#     save_csv: bool = Form(False)
# ):
#     """
#     Accepts a CSV file and preprocesses it.
#     """
#     try:
#         contents = await file.read()
#         df = pd.read_csv(io.BytesIO(contents))
#         result = preprocess(df, save_artifacts=save_csv)
#         return JSONResponse(content=result)
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": f"Error in preprocessing CSV: {str(e)}"})

# # --------------------------- Excel Endpoint ---------------------------
# @app.post("/run_preprocessing/excel")
# async def run_preprocessing_excel(
#     file: UploadFile = File(...),
#     save_excel: bool = Form(False)
# ):
#     """
#     Accepts an Excel file (.xlsx or .xls) and preprocesses it.
#     """
#     try:
#         contents = await file.read()
#         df = pd.read_excel(io.BytesIO(contents))
#         result = preprocess(df, save_artifacts=save_excel)
#         return JSONResponse(content=result)
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": f"Error in preprocessing Excel: {str(e)}"})

# # --------------------------- Parquet Endpoint (Optional) ---------------------------
# @app.post("/run_preprocessing/parquet")
# async def run_preprocessing_parquet(
#     file: UploadFile = File(...),
#     save_parquet: bool = Form(False)
# ):
#     """
#     Accepts a Parquet file and preprocesses it.
#     """
#     try:
#         contents = await file.read()
#         df = pd.read_parquet(io.BytesIO(contents))
#         result = preprocess(df, save_artifacts=save_parquet)
#         return JSONResponse(content=result)
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"error": f"Error in preprocessing Parquet: {str(e)}"})

# # --------------------------- Run Server ---------------------------
# if __name__ == "__main__":
#     uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)



# from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Query
# from pydantic import BaseModel
# from typing import List, Dict, Optional, Union
# import pandas as pd
# import io
# import os

# # -----------------------------
# # Import agent functions
# # -----------------------------
# try:
#     from preprocessing_agent import preprocess
#     from model_selection_agent import model_selection
#     from training_agent import train_model_agent
#     from evaluation_agent import evaluate_model
#     from report_agent import generate_report
# except ModuleNotFoundError as e:
#     preprocess = model_selection = train_model_agent = evaluate_model = generate_report = None
#     print(f"Agent import error: {e}")

# # -----------------------------
# # FastAPI app
# # -----------------------------
# app = FastAPI(title="🚀 Multi-Agent ML Pipeline API")

# # -----------------------------
# # Root endpoint
# # -----------------------------
# @app.get("/")
# def root():
#     return {"message": "Multi-Agent ML Pipeline API is running!"}

# # -----------------------------
# # Preprocessing Endpoint
# # -----------------------------
# class DataItem(BaseModel):
#     features: Dict[str, Union[str, float, int, bool]]

# class PreprocessingRequest(BaseModel):
#     data: List[DataItem]

# @app.post("/run_preprocessing/json")
# def run_preprocessing_json(request: PreprocessingRequest, save_csv: Optional[bool] = Query(True)):
#     if preprocess is None:
#         raise HTTPException(status_code=500, detail="Preprocessing module not found")

#     # Ensure save_csv is boolean
#     save_csv = str(save_csv).lower() == "true"

#     data_list = [item.features for item in request.data]
#     try:
#         result = preprocess(data_list, save_artifacts=save_csv)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")
#     return result

# @app.post("/run_preprocessing/csv")
# async def run_preprocessing_csv(file: UploadFile = File(...), save_csv: Optional[bool] = Query(True)):
#     if preprocess is None:
#         raise HTTPException(status_code=500, detail="Preprocessing module not found")
#     save_csv = str(save_csv).lower() == "true"

#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files are supported")

#     try:
#         contents = await file.read()
#         df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
#         result = preprocess(df, save_artifacts=save_csv)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
#     return result

# @app.post("/run_preprocessing/excel")
# async def run_preprocessing_excel(file: UploadFile = File(...), save_csv: Optional[bool] = Query(True)):
#     if preprocess is None:
#         raise HTTPException(status_code=500, detail="Preprocessing module not found")
#     save_csv = str(save_csv).lower() == "true"

#     if not (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
#         raise HTTPException(status_code=400, detail="Only Excel files are supported")

#     try:
#         contents = await file.read()
#         df = pd.read_excel(io.BytesIO(contents))
#         result = preprocess(df, save_artifacts=save_csv)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing Excel: {str(e)}")
#     return result

# # -----------------------------
# # Model Selection Endpoint
# # -----------------------------
# @app.post("/model_selection")
# def run_model_selection(data: Dict = Body(...)):
#     if model_selection is None:
#         raise HTTPException(status_code=500, detail="Model Selection module not found")
#     try:
#         result = model_selection(data)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in model selection: {str(e)}")
#     return result

# # -----------------------------
# # Model Training Endpoint
# # -----------------------------
# @app.post("/model_training")
# def run_model_training(data: Dict = Body(...)):
#     if train_model_agent is None:
#         raise HTTPException(status_code=500, detail="Training module not found")
#     try:
#         result = train_model_agent(data['df'], target=data['target'], model_type=data.get('model_type', 'auto'))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in model training: {str(e)}")
#     return result

# # -----------------------------
# # Evaluation Endpoint
# # -----------------------------
# @app.post("/evaluation")
# def run_evaluation(data: Dict = Body(...)):
#     if evaluate_model is None:
#         raise HTTPException(status_code=500, detail="Evaluation module not found")
#     try:
#         result = evaluate_model(data['model'], data['X_test'], data['y_test'])
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in evaluation: {str(e)}")
#     return result

# # -----------------------------
# # Report Generation Endpoint
# # -----------------------------
# @app.post("/report_generation")
# def run_report_generation(data: Dict = Body(...)):
#     if generate_report is None:
#         raise HTTPException(status_code=500, detail="Report Generation module not found")
#     try:
#         path = data.get('save_path', './outputs/training_report.html')
#         result = generate_report(
#             preproc_summary=data.get('preproc_summary', {}),
#             training_summary=data.get('training_summary', {}),
#             evaluation_summary=data.get('evaluation_summary', {}),
#             save_path=path
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in report generation: {str(e)}")
#     return {"report_path": result}



from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Query
from pydantic import BaseModel
from typing import List, Dict, Optional, Union, Any
import pandas as pd
import io
import os

# -----------------------------
# Import agent functions safely
# -----------------------------
try:
    from preprocessing_agent import preprocess
    from model_selection_agent import model_selection
    from training_agent import train_model_agent
    from evaluation_agent import evaluate_model
    from report_agent import generate_report
except ModuleNotFoundError as e:
    preprocess = model_selection = train_model_agent = evaluate_model = generate_report = None
    print(f"⚠️ Agent import error: {e}")

# -----------------------------
# Initialize FastAPI
# -----------------------------
app = FastAPI(title="🚀 Multi-Agent ML Pipeline API")

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {"message": "✅ Multi-Agent ML Pipeline API is running successfully!"}

# -----------------------------
# Request Models
# -----------------------------
class DataItem(BaseModel):
    features: Dict[str, Optional[Union[str, float, int, bool, None]]]

class PreprocessingRequest(BaseModel):
    data: List[DataItem]

# -----------------------------
# Preprocessing Endpoints
# -----------------------------
# @app.post("/run_preprocessing/json")
# def run_preprocessing_json(request: PreprocessingRequest, save_csv: Optional[bool] = Query(True)):
#     if preprocess is None:
#         raise HTTPException(status_code=500, detail="❌ Preprocessing module not found")

#     save_csv = bool(str(save_csv).lower() == "true")

#     try:
#         # Convert incoming data to DataFrame
#         df = pd.DataFrame([item.features for item in request.data])

#         # Replace None (null) with NaN
#         df = df.where(pd.notnull(df), None)

#         # Call your preprocessing function
#         result = preprocess(df, save_artifacts=save_csv)

#         return {"status": "✅ Preprocessing successful", "result": result}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")


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
def run_model_training(data: Dict[str, Any] = Body(...)):
    if train_model_agent is None:
        raise HTTPException(status_code=500, detail="❌ Training module not found")
    try:
        df = pd.DataFrame(data["df"]) if isinstance(data["df"], list) else data["df"]
        target = data.get("target")
        model_type = data.get("model_type", "auto")

        result = train_model_agent(df, target=target, model_type=model_type)
        return {"status": "✅ Model trained successfully", "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in model training: {str(e)}")

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
