from fastapi import APIRouter
from ..schemas.contracts import DataFindIn, DataFindOut, DataCandidate
from ..memory import memory
from ..utils.log import logger

from kaggle import api as kaggle_api
from huggingface_hub import HfApi
from datasets import load_dataset
from ucimlrepo import fetch_ucirepo ## CHANGED: Removed non-existent function
import difflib
import pandas as pd
import os

router = APIRouter(prefix="/data", tags=["finder"])
hf = HfApi()

# ------------------------------------
# Helpers
# ------------------------------------
def allowed(license_name: str, allowlist: list[str]) -> bool:
    """Allow datasets if license matches or is unknown."""
    if not license_name:
        return True
    return any(l in license_name.lower() for l in allowlist)


def keyword_match(text: str, keywords: list[str]) -> bool:
    """Fuzzy + substring match for keywords."""
    text = (text or "").lower()
    for k in keywords:
        k = k.lower()
        if k in text:
            return True
        if difflib.get_close_matches(k, [text], cutoff=0.6):
            return True
    return False


def save_dataframe(df, run_id: str, name: str) -> str:
    """Save dataframe to local path and return path (simulate S3)."""
    folder = f"data/{run_id}"
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{name}.csv"
    df.to_csv(path, index=False)
    return path


# ------------------------------------
# Main Finder Endpoint
# ------------------------------------
@router.post("/find", response_model=DataFindOut)
def find_datasets(body: DataFindIn):
    candidates = []
    query = " ".join(body.keywords)
    logger.info(f"🔎 Searching datasets for query='{query}'")

    # Expand license allowlist
    expanded_allowlist = list(set(body.license_allowlist + [
        "apache-2.0", "apache", "mit", "bsd", "bsd-2-clause", "bsd-3-clause",
        "gpl", "gpl-3.0", "cc0", "cc-by", "cc-by-4.0", "cc-by-sa",
        "open", "public domain", "unknown"
    ]))

    # ------------------------------
    # Kaggle
    # ------------------------------
    if "kaggle" in body.sources:
        try:
            kaggle_api.authenticate()
            datasets = kaggle_api.dataset_list(search=query)
            logger.info(f"Kaggle raw results: {[d.ref for d in datasets[:5]]}")
            for d in datasets[:5]:
                lic = (d.licenseName or "unknown").lower()
                if allowed(lic, expanded_allowlist):
                    candidates.append(
                        DataCandidate(
                            name=d.ref,
                            uri=f"https://www.kaggle.com/datasets/{d.ref}",
                            license=lic,
                            est_rows=d.totalBytes or None,
                            schema={"features": [], "target": None},
                            quality_score=0.75,
                        )
                    )
        except Exception as e:
            logger.warning(f"Kaggle search failed: {e}")

    # ------------------------------
    # HuggingFace Datasets
    # ------------------------------
    if "huggingface" in body.sources:
        try:
            results = hf.list_datasets(search=query, limit=5)
            logger.info(f"HuggingFace raw results: {[d.id for d in results]}")

            for d in results:
                lic = (d.cardData.get("license") if getattr(d, "cardData", None) else "") or "unknown"
                if allowed(str(lic), expanded_allowlist):
                    candidates.append(
                        DataCandidate(
                            name=d.id,
                            uri=f"https://huggingface.co/datasets/{d.id}",
                            license=lic,
                            est_rows=None,
                            schema={"features": [], "target": None},
                            quality_score=0.8,
                        )
                    )
        except Exception as e:
            logger.warning(f"HuggingFace search failed: {e}")

    # ------------------------------
    # UCI Datasets
    # ------------------------------
    if "uci" in body.sources:
        try:
            ## CHANGED: Replaced list_available_datasets with robust JSON fetch
            json_url = 'https://raw.githubusercontent.com/uci-ml-repo/ucimlrepo/main/ucimlrepo/assets/dataset_info.json'
            all_uci_df = pd.read_json(json_url)
            
            # Search both name and abstract for keywords
            search_cols = ['name', 'abstract']
            mask = all_uci_df[search_cols].apply(
                lambda col: col.str.contains('|'.join(body.keywords), case=False, na=False)
            ).any(axis=1)
            hits_df = all_uci_df[mask]

            logger.info(f"UCI raw hits: {len(hits_df)}")

            for index, u in hits_df.head(5).iterrows():
                # ADDED: Store the UCI ID in the name for later use
                dataset_name_with_id = f"uci:{u['name']}:{u['id']}"
                candidates.append(
                    DataCandidate(
                        name=dataset_name_with_id,
                        uri=u.get("repository_url") or "https://archive.ics.uci.edu",
                        license="unknown", # UCI metadata does not consistently provide licenses
                        est_rows=u.get("num_instances"),
                        schema={"features": [], "target": None},
                        quality_score=0.7,
                    )
                )
        except Exception as e:
            logger.warning(f"UCI search failed: {e}")

    # ------------------------------
    # Select best candidate + Download it
    # ------------------------------
    selected = None
    downloaded_path = None
    if candidates:
        best = max(candidates, key=lambda c: c.quality_score)
        
        # Clean the name for use as a filename
        base_name = best.name.split(':')[1] if best.name.startswith("uci:") else best.name
        dataset_name_for_file = base_name.replace("/", "_")

        try:
            if best.name.startswith("uci:"):
                ## CHANGED: Dynamic download logic using the ID
                try:
                    # Extract ID from the name string, e.g., "uci:Heart Disease:45"
                    uci_id = int(best.name.split(':')[-1])
                    logger.info(f"Fetching UCI dataset with ID: {uci_id}")
                    dataset = fetch_ucirepo(id=uci_id)
                    X, y = dataset.data.features, dataset.data.targets
                    df = pd.concat([X, y], axis=1)
                    downloaded_path = save_dataframe(df, body.run_id, dataset_name_for_file)
                except (ValueError, IndexError) as e:
                    logger.warning(f"Could not parse UCI ID from name '{best.name}': {e}")
            
            elif "/" in best.name:  # HuggingFace (identified by slash in name)
                ds = load_dataset(best.name, split="train")
                df = ds.to_pandas()
                downloaded_path = save_dataframe(df, body.run_id, dataset_name_for_file)
            
            # ADDED: A placeholder for Kaggle download logic
            else: # Assumes Kaggle otherwise
                logger.info(f"Downloading Kaggle dataset: {best.name}")
                # kaggle_api.dataset_download_files(best.name, path=f"data/{body.run_id}", unzip=True)
                # downloaded_path = f"data/{body.run_id}/{best.name}"
                logger.warning("Kaggle download logic is not fully implemented.")


        except Exception as e:
            logger.warning(f"Download failed for {best.name}: {e}")

        selected = {
            "name": best.name,
            "downloaded_to": downloaded_path or f"s3://bucket/{body.run_id}/raw.csv",
        }

    out = DataFindOut(candidates=candidates, selected=selected)
    memory.log_event(body.run_id, "data/find", out.model_dump())
    return out