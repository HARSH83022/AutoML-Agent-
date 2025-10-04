from fastapi import APIRouter
from ..schemas.contracts import SynthIn, SynthOut
from ..memory import memory
from ..utils.log import logger
from ..config import settings

import os
import pandas as pd
import numpy as np

# Try importing SDV
try:
    from sdv.tabular import GaussianCopula
    SDV_AVAILABLE = True
except ImportError:
    SDV_AVAILABLE = False

router = APIRouter(prefix="/data", tags=["synthetic"])


@router.post("/synthetic", response_model=SynthOut)
def generate_synthetic(body: SynthIn):
    run_dir = os.path.join(settings.ARTIFACTS_DIR, body.run_id)
    os.makedirs(run_dir, exist_ok=True)

    rows = body.schema_hint.get("rows", 1000)
    cols = body.schema_hint.get("columns", [])

    # ---------------- Generate synthetic data ----------------
    df = None

    if SDV_AVAILABLE and body.method == "sdv_tabular":
        # Create dummy schema from hint
        data = {}
        for col in cols:
            name, ctype = col["name"], col["type"]

            if ctype == "int":
                lo, hi = col.get("range", [0, 100])
                data[name] = np.random.randint(lo, hi, size=200).tolist()
            elif ctype == "float":
                lo, hi = col.get("range", [0.0, 1.0])
                data[name] = np.random.uniform(lo, hi, size=200).tolist()
            elif ctype == "binary":
                imbalance = col.get("imbalance_ratio", 0.5)
                data[name] = np.random.choice(
                    [0, 1], size=200, p=[1 - imbalance, imbalance]
                ).tolist()
            else:
                data[name] = [None] * 200

        base_df = pd.DataFrame(data)

        # Train SDV model
        model = GaussianCopula()
        model.fit(base_df)

        df = model.sample(rows)
        notes = "Generated with SDV GaussianCopula."
    else:
        # NumPy fallback
        data = {}
        for col in cols:
            name, ctype = col["name"], col["type"]

            if ctype == "int":
                lo, hi = col.get("range", [0, 100])
                data[name] = np.random.randint(lo, hi, size=rows).tolist()
            elif ctype == "float":
                lo, hi = col.get("range", [0.0, 1.0])
                data[name] = np.random.uniform(lo, hi, size=rows).tolist()
            elif ctype == "binary":
                imbalance = col.get("imbalance_ratio", 0.5)
                data[name] = np.random.choice(
                    [0, 1], size=rows, p=[1 - imbalance, imbalance]
                ).tolist()
            else:
                data[name] = [None] * rows

        df = pd.DataFrame(data)
        notes = f"Generated with {body.method} (NumPy fallback)."

    # ---------------- Save files ----------------
    dataset_path = os.path.join(run_dir, "synthetic.parquet")
    profile_path = os.path.join(run_dir, "synth_profile.txt")

    df.to_parquet(dataset_path, index=False)

    with open(profile_path, "w") as f:
        f.write(f"Synthetic data generated with {rows} rows and {len(cols)} columns.\n")
        f.write(f"Schema hint: {body.schema_hint}\n")
        f.write(f"Method: {body.method}\n")

    # ---------------- Log & return ----------------
    out = SynthOut(
        dataset_uri=f"s3://{run_dir}/synthetic.parquet",
        profile_uri=f"s3://{run_dir}/synth_profile.txt",
        notes=notes,
    )

    memory.log_event(body.run_id, "data/synthetic", out.model_dump())
    logger.info(f"Synthetic dataset created at {dataset_path}")

    return out
