# app/storage.py
# import os

# def ensure_dirs():
#     os.makedirs("data", exist_ok=True)
#     os.makedirs("artifacts", exist_ok=True)

# def save_artifact(run_id, name, content):
#     ensure_dirs()
#     path = f"artifacts/{run_id}_{name}"
#     if isinstance(content, bytes):
#         with open(path, "wb") as f:
#             f.write(content)
#     else:
#         with open(path, "w") as f:
#             f.write(content)
#     return path


# app/storage.py
import os
import shutil
from typing import Union

ARTIFACT_DIR = os.environ.get("ARTIFACT_DIR", "artifacts")
DATA_DIR = os.environ.get("DATA_DIR", "data")


def ensure_dirs():
    """Create necessary directories if they don't exist"""
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)


def save_artifact(run_id: str, name: str, content: Union[str, bytes]) -> str:
    """
    Save artifact to disk.
    
    Args:
        run_id: Unique run identifier
        name: Artifact filename
        content: Content to save (string or bytes)
    
    Returns:
        Path to saved artifact
    """
    ensure_dirs()
    path = os.path.join(ARTIFACT_DIR, f"{run_id}_{name}")
    
    try:
        if isinstance(content, bytes):
            with open(path, "wb") as f:
                f.write(content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        return path
    except Exception as e:
        raise IOError(f"Failed to save artifact {name}: {e}")


def get_artifact_path(run_id: str, name: str) -> str:
    """Get path to artifact file"""
    return os.path.join(ARTIFACT_DIR, f"{run_id}_{name}")


def artifact_exists(run_id: str, name: str) -> bool:
    """Check if artifact exists"""
    path = get_artifact_path(run_id, name)
    return os.path.exists(path)


def list_artifacts(run_id: str) -> list:
    """List all artifacts for a run"""
    ensure_dirs()
    prefix = f"{run_id}_"
    artifacts = []
    
    try:
        for fname in os.listdir(ARTIFACT_DIR):
            if fname.startswith(prefix):
                artifacts.append(fname)
        return sorted(artifacts)
    except Exception as e:
        print(f"Error listing artifacts: {e}")
        return []


def cleanup_run_artifacts(run_id: str):
    """Delete all artifacts for a specific run"""
    artifacts = list_artifacts(run_id)
    for artifact in artifacts:
        try:
            os.remove(os.path.join(ARTIFACT_DIR, artifact))
        except Exception as e:
            print(f"Error deleting {artifact}: {e}")


def get_disk_usage() -> dict:
    """Get disk usage statistics for artifact directory"""
    try:
        total, used, free = shutil.disk_usage(ARTIFACT_DIR)
        return {
            "total_gb": total / (1024**3),
            "used_gb": used / (1024**3),
            "free_gb": free / (1024**3),
            "percent_used": (used / total) * 100
        }
    except Exception as e:
        return {"error": str(e)}
