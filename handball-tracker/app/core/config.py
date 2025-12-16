from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import ValidationError

class Settings(BaseSettings):
    PROJECT_NAME: str = "Handball-Tracker"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    FIRST_SUPERUSER: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "secret"

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
