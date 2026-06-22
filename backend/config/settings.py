import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Air Quality Edge Assistant"
    DATABASE_URL: str = "sqlite:///./data/airqo.db"
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gemma:2b")
    TOOLS_CONFIG_PATH: str = "backend/config/tools.yaml"
    APIS_CONFIG_PATH: str = "backend/config/apis.yaml"

    class Config:
        env_file = ".env"

settings = Settings()
