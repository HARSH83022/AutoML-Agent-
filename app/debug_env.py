import os
from dotenv import load_dotenv
load_dotenv()

print("LLM_MODE =", os.getenv("LLM_MODE"))
print("HF_MODEL =", os.getenv("HF_MODEL"))
print("OLLAMA_MODEL =", os.getenv("OLLAMA_MODEL"))
