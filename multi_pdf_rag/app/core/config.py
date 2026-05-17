from pathlib import Path
from pydantic_settings import BaseSettings


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHROMA_DB_DIR = str(REPO_ROOT / "data" / "vectordb")
DEFAULT_UPLOAD_DIR = str(REPO_ROOT / "data" / "raw")


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    MODEL_NAME: str
    CHROMA_DB_DIR: str = DEFAULT_CHROMA_DB_DIR
    EMBEDDING_MODEL: str
    UPLOAD_DIR: str = DEFAULT_UPLOAD_DIR

    class Config:
        env_file = REPO_ROOT / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()