from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings managed by Pydantic
    """
    # Server settings
    server_host: str = "127.0.0.1"
    server_port: int = 8000
    server_debug: bool = False
    
    # Browser settings
    browser_headless: bool = False
    browser_timeout: int = 30000  # 30 seconds
    
    # Safety settings
    safety_enabled: bool = True
    allowed_action_types: list = ["click", "type", "navigate", "extract"]
    max_execution_time: int = 300  # 5 minutes
    
    # API settings
    gemini_api_key: Optional[str] = None
    gemini_api_url: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    class Config:
        env_file = ".env"


settings = Settings()