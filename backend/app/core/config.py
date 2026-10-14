from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, ConfigDict

class Settings(BaseSettings):
    ENV: str = "local"
    MONGODB_URI_LOCAL: str = "mongodb://localhost:27017/electrohub_nosql"
    MONGODB_URI_ATLAS: str = "mongodb+srv://username:password@cluster.mongodb.net/electrohub_nosql"
    MONGODB_DB_NAME: str = "electrohub_nosql"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
