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

#

import os
import threading
from datetime import datetime
from typing import Optional

ARTIFACT_DIR = os.environ.get("ARTIFACT_DIR", "artifacts")
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Thread-safe logging
_log_lock = threading.Lock()


def agent_log(run_id: str, message: str, agent: str = "system", level: str = "INFO"):
    """
    Thread-safe logging to artifacts/<run_id>_<agent>_log.txt
    
    Args:
        run_id: Unique run identifier
        message: Log message
        agent: Agent name (system, orchestrator, ps_agent, data_agent, etc.)
        level: Log level (INFO, WARNING, ERROR, DEBUG)
    """
    if not run_id:
        run_id = "no_run"
    
    fname = f"{run_id}_{agent}_log.txt"
    path = os.path.join(ARTIFACT_DIR, fname)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{level}] {message}\n"
    
    try:
        with _log_lock:
            with open(path, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
    except Exception as e:
        # Fallback to console if file logging fails
        print(f"[LOGGER ERROR] Failed to write to {path}: {e}")
        print(f"[{timestamp}] [{level}] {message}")


def get_log_tail(run_id: str, agent: str = "orchestrator", lines: int = 200) -> str:
    """
    Get the last N lines from a log file.
    
    Args:
        run_id: Unique run identifier
        agent: Agent name
        lines: Number of lines to retrieve
    
    Returns:
        Last N lines of the log file as a string
    """
    fname = f"{run_id}_{agent}_log.txt"
    path = os.path.join(ARTIFACT_DIR, fname)
    
    if not os.path.exists(path):
        return ""
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:])
    except Exception as e:
        return f"Error reading log: {e}"


def clear_old_logs(days: int = 90):
    """
    Delete log files older than specified days.
    
    Args:
        days: Number of days to keep logs
    """
    import time
    
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    
    try:
        for fname in os.listdir(ARTIFACT_DIR):
            if fname.endswith("_log.txt"):
                fpath = os.path.join(ARTIFACT_DIR, fname)
                if os.path.getmtime(fpath) < cutoff_time:
                    os.remove(fpath)
                    print(f"Deleted old log: {fname}")
    except Exception as e:
        print(f"Error clearing old logs: {e}")

