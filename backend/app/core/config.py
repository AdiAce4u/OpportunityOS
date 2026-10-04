from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "OpportunityOS"
    version: str = "1.0.0"
    database_url: str = "sqlite:///./opportunityos.db"
    
    # LLM Abstraction Layer
    llm_provider: str = "mock"  # "mock" | "gemini" | "openai" | "anthropic"
    llm_api_key: str = ""
    llm_model: str = "gemini-1.5-flash"
    
    # Autonomous Agent Settings
    target_jobs_count: int = 15
    match_threshold: float = 70.0
    auto_generate_queries_limit: int = 4
    
    # Browser Automation Settings
    allow_browser_submit: bool = True
    browser_headless: bool = True
    browser_slow_mo_ms: int = 100
    
    # App URLs
    app_host: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
