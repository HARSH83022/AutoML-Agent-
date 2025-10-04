from fastapi import APIRouter
from ..schemas.contracts import PSParseIn, DataFindIn, SynthIn
from .ps_agent import understand_problem
from .data_finder import find_datasets
from .synthetic import generate_synthetic
from ..memory import memory
from ..utils.log import logger

router = APIRouter(prefix="/pipeline", tags=["orchestrator"])


# ------------- Step 1: Ask Problem -------------
@router.post("/problem")
def step_problem(body: PSParseIn):
    run_id = body.run_id
    logger.info(f"🧩 Step 1: Problem Understanding for {run_id}")
    prob_out = understand_problem(body)
    memory.log_event(run_id, "pipeline/problem", prob_out.model_dump())

    return {
        "message": "Problem understood ✅. Do you want me to find datasets for this?",
        "problem": prob_out
    }


# ------------- Step 2: Dataset Finder -------------
@router.post("/dataset")
def step_dataset(body: DataFindIn):
    run_id = body.run_id
    logger.info(f"📊 Step 2: Dataset Finder for {run_id}")
    data_out = find_datasets(body)
    memory.log_event(run_id, "pipeline/data", data_out.model_dump())

    if data_out.candidates:
        return {
            "message": "I found some datasets. Do you want me to generate synthetic data as well?",
            "datasets": data_out
        }
    else:
        return {
            "message": "No real datasets found. Should I generate synthetic data instead?",
            "datasets": data_out
        }


# ------------- Step 3: Synthetic Data -------------
@router.post("/synthetic")
def step_synthetic(body: SynthIn):
    run_id = body.run_id
    logger.info(f"🧪 Step 3: Synthetic Data for {run_id}")
    synth_out = generate_synthetic(body)
    memory.log_event(run_id, "pipeline/synthetic", synth_out.model_dump())

    return {
        "message": "Synthetic data generated ✅",
        "synthetic": synth_out
    }
