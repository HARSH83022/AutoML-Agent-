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


from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import pandas as pd
import io
import os
import joblib

# Import your preprocessing function
from preprocessing_agent import preprocess

app = FastAPI(title="Dynamic Preprocessing Agent API")

# ================================
# Root endpoint
# ================================
@app.get("/")
def root():
    return {"message": "🚀 Preprocessing Agent API is running!"}

# ================================
# JSON Input Endpoint
# ================================
class DataItem(BaseModel):
    features: Dict[str, Any]

class PreprocessingRequest(BaseModel):
    data: List[DataItem]

@app.post("/run_preprocessing/json")
def run_preprocessing_json(
    request: PreprocessingRequest,
    target: Optional[str] = Form(None),
    split: Optional[bool] = Form(False),
    imbalance: Optional[bool] = Form(False),
    save_csv: Optional[bool] = Form(True),
    reuse_transformer: Optional[bool] = Form(False)
):
    data_list = [item.features for item in request.data]
    
    # Preprocess the data
    try:
        result = preprocess(
            data=data_list,
            target=target,
            split=split,
            imbalance=imbalance,
            save_artifacts=save_csv
        )
        # If reuse_transformer is True, load previous transformer
        if reuse_transformer and os.path.exists("./outputs/latest_transformer.joblib"):
            transformer = joblib.load("./outputs/latest_transformer.joblib")
            df = pd.DataFrame(data_list)
            df_processed = transformer.transform(df)
            result["processed_data"] = pd.DataFrame(
                df_processed, columns=transformer.get_feature_names_out()
            ).to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in preprocessing: {str(e)}")
    
    # Save transformer as latest for reuse
    if save_csv:
        os.makedirs("./outputs", exist_ok=True)
        joblib.dump(result.get("artifacts", {}).get("transformer_uri"), "./outputs/latest_transformer.joblib")
    
    return result

# ================================
# CSV File Upload Endpoint
# ================================
@app.post("/run_preprocessing/csv")
async def run_preprocessing_csv(
    file: UploadFile = File(...),
    target: Optional[str] = Form(None),
    split: Optional[bool] = Form(False),
    imbalance: Optional[bool] = Form(False),
    save_csv: Optional[bool] = Form(True),
    reuse_transformer: Optional[bool] = Form(False)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Reuse previous transformer if required
        if reuse_transformer and os.path.exists("./outputs/latest_transformer.joblib"):
            transformer = joblib.load("./outputs/latest_transformer.joblib")
            df_processed = transformer.transform(df)
            processed_data = pd.DataFrame(
                df_processed, columns=transformer.get_feature_names_out()
            ).to_dict(orient="records")
            result = {"processed_data": processed_data}
        else:
            # Preprocess normally
            result = preprocess(
                data=df,
                target=target,
                split=split,
                imbalance=imbalance,
                save_artifacts=save_csv
            )
            # Save transformer as latest
            if save_csv:
                os.makedirs("./outputs", exist_ok=True)
                joblib.dump(result.get("artifacts", {}).get("transformer_uri"), "./outputs/latest_transformer.joblib")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    
    return result
