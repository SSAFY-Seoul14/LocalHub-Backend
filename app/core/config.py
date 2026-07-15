import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# 프로젝트 루트 경로(.env 위치 탐색용)
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # 챗봇용
    API_ENV: str = "production"
    DATABASE_URL: str = "sqlite:///./data/localhub.db"
    OPENAI_API_KEY: str = ""

    DATA_API_URL: str = ""

    # 지도용
    KAKAO_REST_API_KEY: str = ""

    # Pydantic SettingsConfigDict
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()