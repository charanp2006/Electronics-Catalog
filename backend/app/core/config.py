from typing import List
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    ENV: str = "local"
    MONGODB_URI_LOCAL: str = "mongodb://localhost:27017/electrohub_nosql"
    MONGODB_URI_ATLAS: str = "mongodb+srv://username:password@cluster.mongodb.net/electrohub_nosql"
    MONGODB_DB_NAME: str = "electrohub_nosql"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    SECRET_KEY: str = "electrohub-dev-secret-key-change-in-production-please"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Admin CMS
    ADMIN_SESSION_COOKIE: str = "admin_session"
    ADMIN_CSRF_COOKIE: str = "admin_csrf"
    ADMIN_COOKIE_SECURE: bool = False
    ADMIN_LOGIN_RATE_LIMIT: int = 10
    ADMIN_LOGIN_RATE_WINDOW_MINUTES: int = 15

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def mongo_uri(self) -> str:
        if self.ENV.lower() == "atlas":
            return self.MONGODB_URI_ATLAS
        return self.MONGODB_URI_LOCAL


settings = Settings()
