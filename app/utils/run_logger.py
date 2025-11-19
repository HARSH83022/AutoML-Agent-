# # app/utils/run_logger.py
# import os
# import threading
# import time

# ARTIFACT_DIR = "artifacts"
# os.makedirs(ARTIFACT_DIR, exist_ok=True)
# _lock = threading.Lock()

# def agent_log(run_id: str, text: str, agent: str = None):
#     """
#     Append a timestamped line to artifacts/{run_id}_{agent}_log.txt
#     (or {run_id}_log.txt if agent is None)
#     """
#     if not run_id:
#         run_id = "no_run"
#     fname = f"{run_id}_log.txt" if not agent else f"{run_id}_{agent}_log.txt"
#     path = os.path.join(ARTIFACT_DIR, fname)
#     ts = time.strftime("%Y-%m-%d %H:%M:%S")
#     line = f"[{ts}] {text}\n"
#     with _lock:
#         with open(path, "a", encoding="utf-8") as f:
#             f.write(line)


# app/utils/run_logger.py
import os
import threading
import time
import logging

ARTIFACT_DIR = "artifacts"
os.makedirs(ARTIFACT_DIR, exist_ok=True)
_lock = threading.Lock()

def agent_log(run_id: str, text: str, agent: str = None, level: str = "INFO"):
    if not run_id: run_id = "no_run"
    fname = f"{run_id}_log.txt" if not agent else f"{run_id}_{agent}_log.txt"
    path = os.path.join(ARTIFACT_DIR, fname)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {text}\n"
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)
    # also print to console for convenience
    if level == "ERROR":
        print(f"[{agent}][{run_id}][ERROR] {text}")
    else:
        print(f"[{agent}][{run_id}][INFO] {text}")
