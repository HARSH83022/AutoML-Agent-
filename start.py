#!/usr/bin/env python3
import os
import subprocess

# Get PORT from environment, default to 8000
port = os.environ.get("PORT", "8000")

print(f"[START.PY] PORT environment variable: {port}")
print(f"[START.PY] Starting uvicorn on 0.0.0.0:{port}")

# Use subprocess instead of os.system for better control
subprocess.run([
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", port
])
