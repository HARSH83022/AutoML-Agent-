from dotenv import load_dotenv
import os

# load variables from .env
load_dotenv()

print("✅ GEMINI API key present:", bool(os.getenv("GEMINI_API_KEY")))
print("KAGGLE_USERNAME:", os.getenv("KAGGLE_USERNAME"))
print("ARTIFACTS_DIR:", os.getenv("ARTIFACTS_DIR"))
