from pydantic_settings import BaseSettings
from typing import List
import os
class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    ALLOWED_ORIGINS: str = "*"

    # Security
    PBKDF2_ITERATIONS: int = 150_000
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
CORS_ALLOW_ORIGINS = settings.allowed_origins_list or ["*"]
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
