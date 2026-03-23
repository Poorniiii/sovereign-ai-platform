from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings

# Resolve .env from repo root regardless of where uvicorn is launched from
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"

_ALLOWED_ALGORITHMS = {"HS256", "HS384", "HS512"}


class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    opa_url: str = "http://localhost:8181"
    langgraph_url: str = "http://localhost:8001"
    # Demo user passwords — required, loaded from .env, never hardcoded
    alice_password: str
    bob_password: str

    @model_validator(mode="after")
    def _validate_jwt_settings(self) -> "Settings":
        if self.algorithm not in _ALLOWED_ALGORITHMS:
            raise ValueError(
                f"algorithm '{self.algorithm}' is not allowed; "
                f"must be one of {sorted(_ALLOWED_ALGORITHMS)}"
            )
        if self.access_token_expire_minutes <= 0:
            raise ValueError(
                f"access_token_expire_minutes must be > 0, "
                f"got {self.access_token_expire_minutes}"
            )
        return self

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()
