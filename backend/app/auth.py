from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings

# Demo users — passwords loaded from .env, never hardcoded in source
# Hashed once at module load time so bcrypt's cost is paid only on startup
USERS = {
    "alice": {
        "username": "alice",
        "role": "developer",
        "hashed_password": bcrypt.hashpw(settings.alice_password.encode(), bcrypt.gensalt()),
    },
    "bob": {
        "username": "bob",
        "role": "admin",
        "hashed_password": bcrypt.hashpw(settings.bob_password.encode(), bcrypt.gensalt()),
    },
}


def verify_password(plain: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed)


def get_user(username: str) -> dict | None:
    return USERS.get(username)


def authenticate_user(username: str, password: str) -> dict | None:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
