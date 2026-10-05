import os
from functools import lru_cache
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = dict

class Settings(BaseSettings):
    app_name: str = "OpportunityOS"
    version: str = "1.0.0"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./opportunityos.db")
    
    # LLM Abstraction Layer
    llm_provider: str = os.getenv("LLM_PROVIDER", "gemini")
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-flash-latest")
    
    # Autonomous Agent Settings
    target_jobs_count: int = 15
    match_threshold: float = 70.0
    auto_generate_queries_limit: int = 4
    
    # Browser Automation Settings
    allow_browser_submit: bool = True
    browser_headless: bool = False
    browser_slow_mo_ms: int = 100
    
    # App URLs
    app_host: str = os.getenv("APP_HOST", "https://opportunityos1.onrender.com")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
