#!/usr/bin/env python3
import os
import sys

# Get PORT from environment, default to 8000
port = os.environ.get("PORT", "8000")

print(f"Starting application on port {port}")

# Start uvicorn
os.system(f"uvicorn app.main:app --host 0.0.0.0 --port {port}")
