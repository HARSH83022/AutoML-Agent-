"""
Simple server starter script for local development
"""
import os
import uvicorn

if __name__ == "__main__":
    # Read PORT from environment, default to 8000 for local development
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting server on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
