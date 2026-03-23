from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve .env from repo root regardless of where uvicorn is launched from
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    opa_url: str = "http://localhost:8181"
    langgraph_url: str = "http://localhost:8001"
    # Demo user passwords — required, loaded from .env, never hardcoded
    alice_password: str
    bob_password: str

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()
