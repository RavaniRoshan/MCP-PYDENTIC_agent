from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings managed by Pydantic.

    This class defines the configuration for the application, loading values from
    environment variables or a .env file. It includes settings for the server,
    browser, safety features, and API keys.
    """
    # Server settings
    server_host: str = "127.0.0.1"
    """The host on which the server will run."""
    server_port: int = 8000
    """The port on which the server will listen."""
    server_debug: bool = False
    """Flag to enable or disable debug mode."""
    
    # Browser settings
    browser_headless: bool = False
    """Flag to run the browser in headless mode."""
    browser_timeout: int = 30000  # 30 seconds
    """The default timeout for browser operations in milliseconds."""
    
    # Safety settings
    safety_enabled: bool = True
    """Flag to enable or disable safety features."""
    allowed_action_types: list = ["click", "type", "navigate", "extract"]
    """A list of allowed browser action types."""
    max_execution_time: int = 300  # 5 minutes
    """The maximum execution time for a task in seconds."""
    
    # API settings
    gemini_api_key: Optional[str] = None
    """The API key for the Gemini API."""
    gemini_api_url: str = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    """The URL for the Gemini API endpoint."""
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        """The name of the environment file to load settings from."""


settings = Settings()
"""An instance of the Settings class that can be imported and used throughout the application."""