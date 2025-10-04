# app/config.py
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# load .env
load_dotenv()

class Settings(BaseModel):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    KAGGLE_USERNAME: str | None = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY: str | None = os.getenv("KAGGLE_KEY")
    HF_TOKEN: str | None = os.getenv("HF_TOKEN")
    ARTIFACTS_DIR: str = os.getenv("ARTIFACTS_DIR", "artifacts")

settings = Settings()
