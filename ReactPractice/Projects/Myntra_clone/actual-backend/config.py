from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os

class Settings(BaseSettings):
    API_PREFIX: str = "/api"
    DEBUG: bool = False

    DATABASE_URL: Optional[str] = None
    ALLOWED_ORIGINS: str = "" 

    # Security
    PBKDF2_ITERATIONS: int = 150_000
    SECRET_KEY: str = "change-me"          
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Local SQLite fallback
    DB_PATH: str = "items.db"

    def model_post_init(self, _ctx):
        if not self.DATABASE_URL:
            if self.DEBUG:
                self.DATABASE_URL = f"sqlite:///{self.DB_PATH}"
            else:
                db_user = os.getenv("DB_USER")
                db_password = os.getenv("DB_PASSWORD")
                db_host = os.getenv("DB_HOST", "localhost")
                db_port = os.getenv("DB_PORT", "5432")
                db_name = os.getenv("DB_NAME")
                if all([db_user, db_password, db_host, db_port, db_name]):
                    self.DATABASE_URL = f"postgresql+psycopg://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                else:
                    self.DATABASE_URL = f"sqlite:///{self.DB_PATH}"

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return [o.strip() for o in v.split(",") if o.strip()] if v else []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()

# CORS
CORS_ALLOW_ORIGINS = ["*"]
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]
