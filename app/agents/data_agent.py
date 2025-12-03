# app/agents/data_agent.py
"""
Data Agent - Handles dataset acquisition from multiple sources with fallback chain.

Priority order:
1. User-uploaded file
2. Kaggle API
3. HuggingFace Datasets
4. UCI ML Repository
5. Synthetic generation (fallback)
"""

import os
import json
import requests
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

from app.utils.run_logger import agent_log
from app.utils.llm_clients import llm_generate_json

# Data directory
DATA_DIR = os.environ.get("DATA_DIR", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# API credentials
KAGGLE_USERNAME = os.environ.get("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.environ.get("KAGGLE_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")


# ===============================
# LLM-GUIDED SEARCH QUERY GENERATION
# ===============================
def _generate_search_queries(run_id: str, ps: Dict) -> List[str]:
    """
    Use LLM to generate optimal search queries based on problem statement.
    
    Returns:
        List of 3-5 search query strings
    """
    prompt = f"""
You are a dataset search expert. Generate 3-5 search queries to find relevant tabular datasets.

Problem Statement: {ps.get('raw_text', '')}
Domain: {ps.get('domain', 'general')}
Keywords: {ps.get('keywords', [])}
Task Type: {ps.get('task_type', 'classification')}

Return ONLY valid JSON:
{{
  "queries": ["query1", "query2", "query3"]
}}

Make queries specific and relevant to the problem domain.
"""
    
    try:
        result = llm_generate_json(prompt, max_tokens=256)
        if result and "queries" in result:
            queries = result["queries"][:5]
            agent_log(run_id, f"[data_agent] LLM generated queries: {queries}", agent="data_agent")
            return queries
    except Exception as e:
        agent_log(run_id, f"[data_agent] LLM query generation failed: {e}", agent="data_agent", level="WARNING")
    
    # Fallback: use keywords and domain
    fallback_queries = []
    keywords = ps.get('keywords', [])
    domain = ps.get('domain', '')
    task_type = ps.get('task_type', 'classification')
    
    if keywords:
        fallback_queries.append(" ".join(keywords[:3]))
    if domain:
        fallback_queries.append(f"{domain} {task_type} dataset")
    fallback_queries.append(ps.get('raw_text', 'dataset')[:50])
    
    return [q for q in fallback_queries if q.strip()][:3]


# ===============================
# KAGGLE INTEGRATION
# ===============================
def _search_kaggle(run_id: str, query: str, max_results: int = 5) -> List[Dict]:
    """
    Search Kaggle datasets.
    
    Returns:
        List of dataset metadata dicts
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        import json
        from pathlib import Path
        
        # Ensure credentials are set up
        kaggle_username = os.environ.get("KAGGLE_USERNAME")
        kaggle_key = os.environ.get("KAGGLE_KEY")
        
        if kaggle_username and kaggle_key:
            kaggle_dir = Path.home() / ".kaggle"
            kaggle_json_path = kaggle_dir / "kaggle.json"
            
            if not kaggle_json_path.exists():
                agent_log(run_id, "[data_agent] Creating Kaggle credentials file", agent="data_agent")
                kaggle_dir.mkdir(exist_ok=True)
                credentials = {
                    "username": kaggle_username,
                    "key": kaggle_key
                }
                with open(kaggle_json_path, 'w') as f:
                    json.dump(credentials, f, indent=2)
                try:
                    os.chmod(kaggle_json_path, 0o600)
                except:
                    pass
        
        api = KaggleApi()
        api.authenticate()
        
        agent_log(run_id, f"[data_agent] 🔍 Searching Kaggle: '{query}'", agent="data_agent")
        
        datasets = api.dataset_list(search=query, page=1, max_size=max_results)
        
        results = []
        for ds in datasets:
            # Get attributes safely (some may not exist)
            size_bytes = getattr(ds, 'totalBytes', 0) or getattr(ds, 'size', 0)
            download_count = getattr(ds, 'downloadCount', 0)
            
            results.append({
                "source": "kaggle",
                "ref": ds.ref,
                "title": ds.title,
                "size": size_bytes,
                "downloads": download_count,
                "url": f"https://www.kaggle.com/datasets/{ds.ref}"
            })
        
        agent_log(run_id, f"[data_agent] ✅ Found {len(results)} Kaggle datasets for '{query}'", agent="data_agent")
        if results:
            for i, r in enumerate(results[:3]):
                agent_log(run_id, f"[data_agent]    {i+1}. {r['ref']} - {r['title'][:50]}", agent="data_agent")
        
        return results
        
    except ImportError:
        agent_log(run_id, "[data_agent] ❌ Kaggle library not installed", agent="data_agent", level="WARNING")
        return []
    except Exception as e:
        agent_log(run_id, f"[data_agent] ❌ Kaggle search failed: {e}", agent="data_agent", level="ERROR")
        import traceback
        agent_log(run_id, f"[data_agent] Traceback: {traceback.format_exc()}", agent="data_agent", level="ERROR")
        return []


def _download_kaggle_dataset(run_id: str, dataset_ref: str) -> Optional[str]:
    """
    Download Kaggle dataset and return path to CSV file.
    
    Args:
        run_id: Run identifier
        dataset_ref: Kaggle dataset reference (e.g., "username/dataset-name")
    
    Returns:
        Path to downloaded CSV file or None
    """
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        api = KaggleApi()
        api.authenticate()
        
        out_dir = os.path.join(DATA_DIR, f"{run_id}_kaggle_{dataset_ref.replace('/', '_')}")
        os.makedirs(out_dir, exist_ok=True)
        
        agent_log(run_id, f"[data_agent] 📥 Downloading Kaggle dataset: {dataset_ref}", agent="data_agent")
        
        # Download with error handling
        try:
            api.dataset_download_files(dataset_ref, path=out_dir, unzip=True, quiet=False)
        except Exception as download_error:
            agent_log(run_id, f"[data_agent] Download error: {download_error}", agent="data_agent", level="ERROR")
            return None
        
        # Find CSV files
        csv_files = list(Path(out_dir).glob("**/*.csv"))
        
        if not csv_files:
            # List what files we got
            all_files = list(Path(out_dir).glob("**/*"))
            file_names = [f.name for f in all_files if f.is_file()]
            agent_log(run_id, f"[data_agent] ⚠️ No CSV files found in {dataset_ref}", agent="data_agent", level="WARNING")
            agent_log(run_id, f"[data_agent] Files found: {', '.join(file_names[:10])}", agent="data_agent", level="WARNING")
            return None
        
        # Return the largest CSV file
        largest_csv = max(csv_files, key=lambda p: p.stat().st_size)
        csv_path = str(largest_csv)
        
        # Validate CSV
        try:
            df = pd.read_csv(csv_path, nrows=5)
            file_size = largest_csv.stat().st_size
            agent_log(run_id, f"[data_agent] ✅ Kaggle dataset downloaded: {csv_path}", agent="data_agent")
            agent_log(run_id, f"[data_agent]    File: {largest_csv.name} ({file_size} bytes, {len(df.columns)} columns)", agent="data_agent")
            return csv_path
        except Exception as e:
            agent_log(run_id, f"[data_agent] ❌ Invalid CSV file: {e}", agent="data_agent", level="ERROR")
            return None
            
    except Exception as e:
        agent_log(run_id, f"[data_agent] ❌ Kaggle download failed: {e}", agent="data_agent", level="ERROR")
        import traceback
        agent_log(run_id, f"[data_agent] Traceback: {traceback.format_exc()}", agent="data_agent", level="ERROR")
        return None


# ===============================
# HUGGINGFACE INTEGRATION
# ===============================
def _search_huggingface(run_id: str, query: str, max_results: int = 5) -> List[Dict]:
    """
    Search HuggingFace datasets.
    
    Returns:
        List of dataset metadata dicts
    """
    try:
        from huggingface_hub import list_datasets
        
        agent_log(run_id, f"[data_agent] Searching HuggingFace: '{query}'", agent="data_agent")
        
        # Search datasets
        datasets = list(list_datasets(search=query, limit=max_results))
        
        results = []
        for ds in datasets:
            dataset_id = ds.id if hasattr(ds, 'id') else str(ds)
            results.append({
                "source": "huggingface",
                "id": dataset_id,
                "url": f"https://huggingface.co/datasets/{dataset_id}"
            })
        
        agent_log(run_id, f"[data_agent] Found {len(results)} HuggingFace datasets", agent="data_agent")
        return results
        
    except ImportError:
        agent_log(run_id, "[data_agent] HuggingFace hub not installed", agent="data_agent", level="WARNING")
        return []
    except Exception as e:
        agent_log(run_id, f"[data_agent] HuggingFace search failed: {e}", agent="data_agent", level="ERROR")
        return []


def _download_huggingface_dataset(run_id: str, dataset_id: str, max_rows: int = 50000) -> Optional[str]:
    """
    Download HuggingFace dataset and convert to CSV.
    
    Args:
        run_id: Run identifier
        dataset_id: HuggingFace dataset ID
        max_rows: Maximum rows to download
    
    Returns:
        Path to CSV file or None
    """
    try:
        from datasets import load_dataset
        
        agent_log(run_id, f"[data_agent] Loading HuggingFace dataset: {dataset_id}", agent="data_agent")
        
        # Load dataset
        dataset = load_dataset(dataset_id, split="train")
        
        # Convert to pandas
        df = dataset.to_pandas()
        
        # Limit rows
        if len(df) > max_rows:
            agent_log(run_id, f"[data_agent] Sampling {max_rows} rows from {len(df)}", agent="data_agent")
            df = df.sample(n=max_rows, random_state=42)
        
        # Save to CSV
        safe_name = dataset_id.replace("/", "_").replace(":", "_")
        csv_path = os.path.join(DATA_DIR, f"{run_id}_hf_{safe_name}.csv")
        df.to_csv(csv_path, index=False)
        
        agent_log(run_id, f"[data_agent] HuggingFace dataset saved: {csv_path} ({len(df)} rows, {len(df.columns)} columns)", agent="data_agent")
        return csv_path
        
    except Exception as e:
        agent_log(run_id, f"[data_agent] HuggingFace download failed: {e}", agent="data_agent", level="ERROR")
        return None


# ===============================
# UCI ML REPOSITORY INTEGRATION
# ===============================
def _search_uci(run_id: str, query: str) -> List[Dict]:
    """
    Search UCI ML Repository (simplified - uses keyword matching).
    
    Returns:
        List of dataset metadata dicts
    """
    # UCI dataset catalog (subset of popular datasets)
    UCI_DATASETS = {
        "iris": "https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data",
        "wine": "https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data",
        "breast cancer": "https://archive.ics.uci.edu/ml/machine-learning-databases/breast-cancer-wisconsin/wdbc.data",
        "adult": "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data",
        "diabetes": "https://archive.ics.uci.edu/ml/machine-learning-databases/00296/dataset_diabetes.zip",
        "heart": "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data",
        "credit": "https://archive.ics.uci.edu/ml/machine-learning-databases/credit-screening/crx.data",
    }
    
    query_lower = query.lower()
    results = []
    
    for name, url in UCI_DATASETS.items():
        if any(word in name for word in query_lower.split()):
            results.append({
                "source": "uci",
                "name": name,
                "url": url
            })
    
    agent_log(run_id, f"[data_agent] Found {len(results)} UCI datasets matching '{query}'", agent="data_agent")
    return results


def _download_uci_dataset(run_id: str, dataset_url: str, dataset_name: str) -> Optional[str]:
    """
    Download UCI dataset.
    
    Args:
        run_id: Run identifier
        dataset_url: URL to dataset
        dataset_name: Name of dataset
    
    Returns:
        Path to CSV file or None
    """
    try:
        agent_log(run_id, f"[data_agent] Downloading UCI dataset: {dataset_name}", agent="data_agent")
        
        response = requests.get(dataset_url, timeout=30)
        response.raise_for_status()
        
        # Save to CSV
        csv_path = os.path.join(DATA_DIR, f"{run_id}_uci_{dataset_name.replace(' ', '_')}.csv")
        
        # Try to parse as CSV
        from io import StringIO
        df = pd.read_csv(StringIO(response.text), header=None)
        df.to_csv(csv_path, index=False)
        
        agent_log(run_id, f"[data_agent] UCI dataset saved: {csv_path} ({len(df)} rows)", agent="data_agent")
        return csv_path
        
    except Exception as e:
        agent_log(run_id, f"[data_agent] UCI download failed: {e}", agent="data_agent", level="ERROR")
        return None


# ===============================
# SYNTHETIC DATA GENERATION
# ===============================
def _generate_synthetic_dataset(run_id: str, ps: Dict, n_rows: int = 2000) -> str:
    """
    Generate synthetic tabular dataset using LLM-guided schema.
    
    Args:
        run_id: Run identifier
        ps: Problem statement dict
        n_rows: Number of rows to generate
    
    Returns:
        Path to generated CSV file
    """
    agent_log(run_id, "[data_agent] Generating synthetic dataset", agent="data_agent")
    
    # Ask LLM for schema
    prompt = f"""
You are a synthetic data generator. Create a schema for a tabular dataset.

Problem: {ps.get('raw_text', '')}
Task Type: {ps.get('task_type', 'classification')}
Domain: {ps.get('domain', 'general')}

Return ONLY valid JSON with this structure:
{{
  "columns": [
    {{"name": "age", "type": "int", "min": 18, "max": 80}},
    {{"name": "income", "type": "float", "min": 20000, "max": 150000}},
    {{"name": "category", "type": "categorical", "values": ["A", "B", "C"]}}
  ],
  "target": {{"name": "target", "type": "binary"}}
}}

Include 5-10 relevant features for the problem.
"""
    
    try:
        schema = llm_generate_json(prompt, max_tokens=512)
        if not schema or "columns" not in schema:
            raise ValueError("Invalid schema from LLM")
    except Exception as e:
        agent_log(run_id, f"[data_agent] LLM schema generation failed: {e}, using default", agent="data_agent", level="WARNING")
        # Default schema
        schema = {
            "columns": [
                {"name": "feature1", "type": "float", "min": 0, "max": 1},
                {"name": "feature2", "type": "int", "min": 1, "max": 100},
                {"name": "feature3", "type": "float", "min": -10, "max": 10},
                {"name": "feature4", "type": "categorical", "values": ["A", "B", "C", "D"]},
            ],
            "target": {"name": "target", "type": "binary"}
        }
    
    # Generate data
    data = {}
    
    for col in schema.get("columns", []):
        col_name = col["name"]
        col_type = col["type"]
        
        if col_type == "int":
            data[col_name] = np.random.randint(col.get("min", 0), col.get("max", 100), n_rows)
        elif col_type == "float":
            data[col_name] = np.random.uniform(col.get("min", 0), col.get("max", 1), n_rows)
        elif col_type == "categorical":
            values = col.get("values", ["A", "B", "C"])
            data[col_name] = np.random.choice(values, n_rows)
    
    # Generate target
    target_info = schema.get("target", {"name": "target", "type": "binary"})
    target_name = target_info["name"]
    target_type = target_info["type"]
    
    if target_type == "binary":
        data[target_name] = np.random.randint(0, 2, n_rows)
    elif target_type == "multiclass":
        n_classes = target_info.get("n_classes", 3)
        data[target_name] = np.random.randint(0, n_classes, n_rows)
    else:  # regression
        data[target_name] = np.random.randn(n_rows)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    csv_path = os.path.join(DATA_DIR, f"{run_id}_synthetic.csv")
    df.to_csv(csv_path, index=False)
    
    agent_log(run_id, f"[data_agent] Synthetic dataset generated: {csv_path} ({len(df)} rows, {len(df.columns)} columns)", agent="data_agent")
    return csv_path


# ===============================
# DATASET VALIDATION
# ===============================
def _validate_dataset(run_id: str, csv_path: str, min_rows: int = 50, min_cols: int = 2) -> Tuple[bool, Dict]:
    """
    Validate dataset meets minimum requirements.
    
    Returns:
        (is_valid, summary_dict)
    """
    try:
        df = pd.read_csv(csv_path, nrows=100)
        
        n_rows_sample = len(df)
        n_cols = len(df.columns)
        
        # Check full row count
        with open(csv_path, 'r') as f:
            n_rows = sum(1 for _ in f) - 1  # Subtract header
        
        summary = {
            "n_rows": n_rows,
            "n_cols": n_cols,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_pct": {col: float(df[col].isna().mean()) for col in df.columns},
            "path": csv_path
        }
        
        is_valid = n_rows >= min_rows and n_cols >= min_cols
        
        if is_valid:
            agent_log(run_id, f"[data_agent] Dataset validated: {n_rows} rows, {n_cols} columns", agent="data_agent")
        else:
            agent_log(run_id, f"[data_agent] Dataset validation failed: {n_rows} rows, {n_cols} columns", agent="data_agent", level="WARNING")
        
        return is_valid, summary
        
    except Exception as e:
        agent_log(run_id, f"[data_agent] Dataset validation error: {e}", agent="data_agent", level="ERROR")
        return False, {}


# ===============================
# MAIN ORCHESTRATION FUNCTION
# ===============================
def get_or_find_dataset(run_id: str, ps: Dict, user: Dict) -> Dict:
    """
    Main entry point for data acquisition.
    
    Tries sources in priority order:
    1. User-uploaded file
    2. Kaggle
    3. HuggingFace
    4. UCI ML Repository
    5. Synthetic generation (fallback)
    
    Args:
        run_id: Unique run identifier
        ps: Problem statement dict
        user: User payload dict (may contain upload_path)
    
    Returns:
        Dict with dataset_path, source, and source_name
    """
    agent_log(run_id, "[data_agent] Starting dataset acquisition", agent="data_agent")
    
    print(f"\n{'='*60}")
    print(f"🔍 SEARCHING FOR DATASETS")
    print(f"   Problem: {ps.get('raw_text', 'N/A')[:50]}...")
    print(f"   Task Type: {ps.get('task_type', 'unknown')}")
    print(f"   Domain: {ps.get('domain', 'general')}")
    print(f"\n   Search Order:")
    print(f"   1. User Upload")
    print(f"   2. Kaggle")
    print(f"   3. HuggingFace")
    print(f"   4. UCI ML Repository")
    print(f"   5. Synthetic (fallback)")
    print(f"{'='*60}\n")
    
    # ===== 1. USER-UPLOADED FILE =====
    if user and user.get("upload_path"):
        upload_path = user["upload_path"]
        agent_log(run_id, f"[data_agent] Using user-uploaded file: {upload_path}", agent="data_agent")
        
        if os.path.exists(upload_path):
            is_valid, summary = _validate_dataset(run_id, upload_path)
            if is_valid:
                print(f"\n{'='*60}")
                print(f"✅ DATASET SELECTED: User Upload")
                print(f"   File: {upload_path}")
                print(f"   Rows: {summary.get('n_rows', 'unknown')}")
                print(f"   Columns: {summary.get('n_cols', 'unknown')}")
                print(f"{'='*60}\n")
                agent_log(run_id, f"[data_agent] ✅ USING USER-UPLOADED FILE: {upload_path} ({summary.get('n_rows')} rows, {summary.get('n_cols')} cols)", agent="data_agent")
                return {
                    "dataset_path": upload_path,
                    "source": "User Upload",
                    "source_name": os.path.basename(upload_path)
                }
            else:
                agent_log(run_id, "[data_agent] User file invalid, trying other sources", agent="data_agent", level="WARNING")
        else:
            agent_log(run_id, f"[data_agent] User file not found: {upload_path}", agent="data_agent", level="ERROR")
    
    # Generate search queries
    queries = _generate_search_queries(run_id, ps)
    agent_log(run_id, f"[data_agent] Search queries: {queries}", agent="data_agent")
    
    # Add well-known public datasets as fallback based on task type
    task_type = ps.get('task_type', 'classification')
    domain = ps.get('domain', '').lower()
    
    # Known good public datasets on Kaggle
    known_datasets = []
    if 'iris' in domain or 'flower' in domain:
        known_datasets.append('uciml/iris')
    if 'diabetes' in domain or 'health' in domain:
        known_datasets.append('uciml/pima-indians-diabetes-database')
    if 'cancer' in domain or 'breast' in domain:
        known_datasets.append('uciml/breast-cancer-wisconsin-data')
    if 'wine' in domain:
        known_datasets.append('uciml/red-wine-quality-cortez-et-al-2009')
    
    # ===== 2. KAGGLE =====
    # First try search results
    for query in queries:
        try:
            kaggle_results = _search_kaggle(run_id, query, max_results=3)
            for result in kaggle_results:
                csv_path = _download_kaggle_dataset(run_id, result["ref"])
                if csv_path:
                    is_valid, summary = _validate_dataset(run_id, csv_path)
                    if is_valid:
                        print(f"\n{'='*60}")
                        print(f"✅ DATASET SELECTED: Kaggle")
                        print(f"   Dataset: {result['ref']}")
                        print(f"   Rows: {summary.get('n_rows', 'unknown')}")
                        print(f"   Columns: {summary.get('n_cols', 'unknown')}")
                        print(f"   Path: {csv_path}")
                        print(f"{'='*60}\n")
                        agent_log(run_id, f"[data_agent] ✅ SELECTED KAGGLE DATASET: {result['ref']} ({summary.get('n_rows')} rows, {summary.get('n_cols')} cols)", agent="data_agent")
                        return {
                            "dataset_path": csv_path,
                            "source": "Kaggle",
                            "source_name": result['ref'],
                            "source_url": result.get('url', '')
                        }
        except Exception as e:
            agent_log(run_id, f"[data_agent] Kaggle attempt failed: {e}", agent="data_agent", level="WARNING")
            continue
    
    # Try known public datasets as fallback
    if known_datasets:
        agent_log(run_id, f"[data_agent] Trying known public datasets: {known_datasets}", agent="data_agent")
        for dataset_ref in known_datasets:
            try:
                csv_path = _download_kaggle_dataset(run_id, dataset_ref)
                if csv_path:
                    is_valid, summary = _validate_dataset(run_id, csv_path)
                    if is_valid:
                        print(f"\n{'='*60}")
                        print(f"✅ DATASET SELECTED: Kaggle (Known Public Dataset)")
                        print(f"   Dataset: {dataset_ref}")
                        print(f"   Rows: {summary.get('n_rows', 'unknown')}")
                        print(f"   Columns: {summary.get('n_cols', 'unknown')}")
                        print(f"   Path: {csv_path}")
                        print(f"{'='*60}\n")
                        agent_log(run_id, f"[data_agent] ✅ SELECTED KAGGLE DATASET: {dataset_ref} ({summary.get('n_rows')} rows, {summary.get('n_cols')} cols)", agent="data_agent")
                        return {
                            "dataset_path": csv_path,
                            "source": "Kaggle",
                            "source_name": dataset_ref,
                            "source_url": f"https://www.kaggle.com/datasets/{dataset_ref}"
                        }
            except Exception as e:
                agent_log(run_id, f"[data_agent] Known dataset {dataset_ref} failed: {e}", agent="data_agent", level="WARNING")
                continue
    
    # ===== 3. HUGGINGFACE =====
    for query in queries:
        try:
            hf_results = _search_huggingface(run_id, query, max_results=3)
            for result in hf_results:
                csv_path = _download_huggingface_dataset(run_id, result["id"])
                if csv_path:
                    is_valid, summary = _validate_dataset(run_id, csv_path)
                    if is_valid:
                        print(f"\n{'='*60}")
                        print(f"✅ DATASET SELECTED: HuggingFace")
                        print(f"   Dataset: {result['id']}")
                        print(f"   Rows: {summary.get('n_rows', 'unknown')}")
                        print(f"   Columns: {summary.get('n_cols', 'unknown')}")
                        print(f"   Path: {csv_path}")
                        print(f"{'='*60}\n")
                        agent_log(run_id, f"[data_agent] ✅ SELECTED HUGGINGFACE DATASET: {result['id']} ({summary.get('n_rows')} rows, {summary.get('n_cols')} cols)", agent="data_agent")
                        return {
                            "dataset_path": csv_path,
                            "source": "HuggingFace",
                            "source_name": result['id'],
                            "source_url": result.get('url', '')
                        }
        except Exception as e:
            agent_log(run_id, f"[data_agent] HuggingFace attempt failed: {e}", agent="data_agent", level="WARNING")
            continue
    
    # ===== 4. UCI ML REPOSITORY =====
    for query in queries:
        try:
            uci_results = _search_uci(run_id, query)
            for result in uci_results:
                csv_path = _download_uci_dataset(run_id, result["url"], result["name"])
                if csv_path:
                    is_valid, summary = _validate_dataset(run_id, csv_path)
                    if is_valid:
                        print(f"\n{'='*60}")
                        print(f"✅ DATASET SELECTED: UCI ML Repository")
                        print(f"   Dataset: {result['name']}")
                        print(f"   Rows: {summary.get('n_rows', 'unknown')}")
                        print(f"   Columns: {summary.get('n_cols', 'unknown')}")
                        print(f"   Path: {csv_path}")
                        print(f"{'='*60}\n")
                        agent_log(run_id, f"[data_agent] ✅ SELECTED UCI DATASET: {result['name']} ({summary.get('n_rows')} rows, {summary.get('n_cols')} cols)", agent="data_agent")
                        return {
                            "dataset_path": csv_path,
                            "source": "UCI ML Repository",
                            "source_name": result['name'],
                            "source_url": result.get('url', '')
                        }
        except Exception as e:
            agent_log(run_id, f"[data_agent] UCI attempt failed: {e}", agent="data_agent", level="WARNING")
            continue
    
    # ===== 5. SYNTHETIC GENERATION (FALLBACK) =====
    print(f"\n{'='*60}")
    print(f"⚠️  FALLBACK: Generating Synthetic Dataset")
    print(f"   Reason: No suitable datasets found from external sources")
    print(f"{'='*60}\n")
    agent_log(run_id, "[data_agent] ⚠️ All external sources failed, generating synthetic dataset", agent="data_agent", level="WARNING")
    
    n_rows = int(os.environ.get("SYNTHETIC_DEFAULT_ROWS", "2000"))
    csv_path = _generate_synthetic_dataset(run_id, ps, n_rows=n_rows)
    
    # Get summary for synthetic data
    is_valid, summary = _validate_dataset(run_id, csv_path)
    
    print(f"\n{'='*60}")
    print(f"✅ DATASET GENERATED: Synthetic")
    print(f"   Rows: {summary.get('n_rows', n_rows)}")
    print(f"   Columns: {summary.get('n_cols', 'unknown')}")
    print(f"   Path: {csv_path}")
    print(f"{'='*60}\n")
    
    return {
        "dataset_path": csv_path,
        "source": "Synthetic (Generated)",
        "source_name": f"Generated for: {ps.get('raw_text', 'ML Task')[:50]}"
    }
