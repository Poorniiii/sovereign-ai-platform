from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings

# Dummy hash used to perform a constant-time bcrypt check when the username
# does not exist, preventing timing-based username enumeration attacks.
# Pre-computed once at module load so it does not add startup cost on each request.
DUMMY_HASH: bytes = bcrypt.hashpw(b"dummy", bcrypt.gensalt())

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
    # Always run bcrypt regardless of whether the user exists.
    # This keeps response time constant and prevents timing-based username enumeration.
    hashed_to_check = user["hashed_password"] if user else DUMMY_HASH
    password_valid = verify_password(password, hashed_to_check)
    if user and password_valid:
        return user
    return None


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
