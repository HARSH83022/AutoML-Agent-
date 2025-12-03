"""
Configuration module for AutoML Orchestrator
Handles environment variables with validation and defaults
"""
import os
from typing import Optional
import sys


class Config:
    """Application configuration from environment variables"""
    
    # ============================================
    # Required Environment Variables
    # ============================================
    # PORT is automatically provided by Render
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # ============================================
    # Application Settings
    # ============================================
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # ============================================
    # Database & Storage
    # ============================================
    DB_PATH: str = os.getenv("DB_PATH", "runs.db")
    ARTIFACT_DIR: str = os.getenv("ARTIFACT_DIR", "artifacts")
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    
    # ============================================
    # LLM Configuration (Optional)
    # ============================================
    LLM_MODE: str = os.getenv("LLM_MODE", "none")
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    # Ollama (Local)
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "mistral:latest")
    
    # HuggingFace
    HF_MODEL: str = os.getenv("HF_MODEL", "google/flan-t5-small")
    HF_TOKEN: Optional[str] = os.getenv("HF_TOKEN")
    
    # ============================================
    # Data Sources (Optional)
    # ============================================
    KAGGLE_USERNAME: Optional[str] = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY: Optional[str] = os.getenv("KAGGLE_KEY")
    
    # ============================================
    # ML Settings
    # ============================================
    SYNTHETIC_DEFAULT_ROWS: int = int(os.getenv("SYNTHETIC_DEFAULT_ROWS", "2000"))
    THREAD_POOL_SIZE: int = int(os.getenv("THREAD_POOL_SIZE", "2"))
    
    # ============================================
    # Python & Node Versions (for Render)
    # ============================================
    PYTHON_VERSION: str = os.getenv("PYTHON_VERSION", "3.11.0")
    NODE_VERSION: str = os.getenv("NODE_VERSION", "18.x")
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate required environment variables.
        Returns True if all required variables are set, False otherwise.
        Prints warnings for missing optional variables.
        """
        is_valid = True
        
        # Check LLM configuration if not in 'none' mode
        if cls.LLM_MODE not in ["none", "ollama", "hf"]:
            if cls.LLM_MODE == "openai" and not cls.OPENAI_API_KEY:
                print("WARNING: LLM_MODE is 'openai' but OPENAI_API_KEY is not set", file=sys.stderr)
                is_valid = False
            elif cls.LLM_MODE == "anthropic" and not cls.ANTHROPIC_API_KEY:
                print("WARNING: LLM_MODE is 'anthropic' but ANTHROPIC_API_KEY is not set", file=sys.stderr)
                is_valid = False
            elif cls.LLM_MODE == "gemini" and not cls.GOOGLE_API_KEY:
                print("WARNING: LLM_MODE is 'gemini' but GOOGLE_API_KEY is not set", file=sys.stderr)
                is_valid = False
        
        # Optional warnings
        if not cls.KAGGLE_USERNAME or not cls.KAGGLE_KEY:
            print("INFO: Kaggle credentials not set - Kaggle dataset downloads will not work", file=sys.stderr)
        
        if not cls.HF_TOKEN:
            print("INFO: HF_TOKEN not set - some HuggingFace features may be limited", file=sys.stderr)
        
        return is_valid
    
    @classmethod
    def get_summary(cls) -> dict:
        """
        Get a summary of current configuration (without sensitive values).
        """
        return {
            "app_env": cls.APP_ENV,
            "log_level": cls.LOG_LEVEL,
            "llm_mode": cls.LLM_MODE,
            "port": cls.PORT,
            "host": cls.HOST,
            "database": cls.DB_PATH,
            "artifact_dir": cls.ARTIFACT_DIR,
            "data_dir": cls.DATA_DIR,
            "synthetic_rows": cls.SYNTHETIC_DEFAULT_ROWS,
            "thread_pool_size": cls.THREAD_POOL_SIZE,
            "kaggle_configured": bool(cls.KAGGLE_USERNAME and cls.KAGGLE_KEY),
            "hf_token_configured": bool(cls.HF_TOKEN),
            "openai_configured": bool(cls.OPENAI_API_KEY),
            "anthropic_configured": bool(cls.ANTHROPIC_API_KEY),
            "google_configured": bool(cls.GOOGLE_API_KEY),
        }


# Validate configuration on import
if __name__ != "__main__":
    Config.validate()
