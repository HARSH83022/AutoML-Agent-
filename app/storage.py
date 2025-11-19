# app/storage.py
import os

def ensure_dirs():
    os.makedirs("data", exist_ok=True)
    os.makedirs("artifacts", exist_ok=True)

def save_artifact(run_id, name, content):
    ensure_dirs()
    path = f"artifacts/{run_id}_{name}"
    if isinstance(content, bytes):
        with open(path, "wb") as f:
            f.write(content)
    else:
        with open(path, "w") as f:
            f.write(content)
    return path
