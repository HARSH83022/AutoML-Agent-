from pydantic import BaseModel
from typing import List, Dict, Optional

# ---------------- Problem Statement ----------------

class PSParseIn(BaseModel):
    run_id: str
    text: str
    preferences: Optional[Dict] = None


class PSParseOut(BaseModel):
    task_type: str
    domain: str
    target: str
    entities: List[str]
    keywords: List[str]
    constraints: Dict
    plan: Dict


class PSGenIn(BaseModel):
    run_id: str
    domain: str
    goal: str
    constraints: Dict = {}


class PSOption(BaseModel):
    title: str
    statement: str
    task_type: str
    metrics: List[str]


class PSGenOut(BaseModel):
    options: List[PSOption]


# ---------------- Dataset Finder ----------------

# ---------------- Dataset Finder ----------------

class DataFindIn(BaseModel):
    run_id: str
    keywords: List[str]
    sources: List[str] = ["kaggle", "huggingface", "uci", "google_dataset_search"]
    license_allowlist: List[str] = ["cc-by", "cc-by-sa", "mit"]
    min_rows: int = 5000


class DataCandidate(BaseModel):
    name: str
    uri: str
    license: Optional[str] = None
    est_rows: Optional[int] = None
    schema: Optional[Dict] = None   # ✅ corrected (was dataset_schema)
    quality_score: Optional[float] = None


class DataFindOut(BaseModel):
    candidates: List[DataCandidate]
    selected: Optional[Dict] = None   # ✅ allows {"name": ..., "downloaded_to": ...}



# ---------------- Synthetic Data ----------------

class SynthIn(BaseModel):
    run_id: str
    reason: str
    schema_hint: Dict
    method: str = "sdv_tabular"


class SynthOut(BaseModel):
    dataset_uri: str
    profile_uri: str
    notes: str
