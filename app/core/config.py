from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = "Templace API"
    VERSION: str = "0.1.0"
    ENV: str = "development"
    DEBUG: bool = True

    TEMPLATES_DIR: Path = Path("templates_storage")
    MAX_TEMPLATE_SIZE_MB: int = 10

    MAX_CONCURRENT_GENERATIONS: int = 10

    class Config:
        env_file = ".env"

settings = Settings()