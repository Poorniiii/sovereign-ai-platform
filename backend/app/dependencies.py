from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

# HTTPBearer extracts the token from "Authorization: Bearer <token>" headers.
# Unlike OAuth2PasswordBearer, it does not declare a tokenUrl, which avoids
# Swagger UI trying to POST form-encoded credentials to /auth/login (our login
# endpoint expects a JSON body, not a form — the two are incompatible).
_bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        return {"sub": username, "role": role}
    except JWTError:
        raise credentials_exception
