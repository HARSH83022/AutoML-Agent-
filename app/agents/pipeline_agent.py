from fastapi import APIRouter, Depends
from ..schemas.contracts import PSParseIn, PSParseOut, DataFindIn, DataFindOut, SynthIn, SynthOut
from ..agents import ps_agent, data_finder, synthetic
from ..memory import memory

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/start")
def start_pipeline(ps_input: PSParseIn):
    """
    Run full pipeline:
    1. Parse problem statement
    2. Find datasets
    3. Generate synthetic data if needed
    """

    # --------------------------
    # Step 1: Problem Understanding
    # --------------------------
    parsed: PSParseOut = ps_agent.parse_ps(ps_input)
    memory.log_event(ps_input.run_id, "pipeline/ps_parse", parsed.model_dump())

    # --------------------------
    # Step 2: Dataset Finder
    # --------------------------
    df_input = DataFindIn(
        run_id=ps_input.run_id,
        keywords=parsed.keywords,
        sources=["kaggle", "huggingface", "uci"],
        license_allowlist=["cc-by", "cc-by-sa", "mit", "apache-2.0", "cc0"],
        min_rows=5000,
    )
    datasets: DataFindOut = data_finder.find_datasets(df_input)
    memory.log_event(ps_input.run_id, "pipeline/data_find", datasets.model_dump())

    # --------------------------
    # Step 3: Synthetic Data (only if no dataset found)
    # --------------------------
    synthetic_out = None
    if not datasets.candidates:
        synth_input = SynthIn(
            run_id=ps_input.run_id,
            reason="No suitable dataset found",
            schema_hint={"features": parsed.entities, "target": parsed.target},
        )
        synthetic_out: SynthOut = synthetic.generate_synthetic(synth_input)
        memory.log_event(ps_input.run_id, "pipeline/synthetic", synthetic_out.model_dump())

    # --------------------------
    # Final response
    # --------------------------
    return {
        "problem_parsed": parsed,
        "datasets": datasets,
        "synthetic": synthetic_out,
    }
