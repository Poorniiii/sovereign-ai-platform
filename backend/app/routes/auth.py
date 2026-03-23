from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.audit import write_audit_entry
from app.auth import authenticate_user, create_access_token

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    role: str  # "developer" or "admin" — used to validate against stored role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = authenticate_user(request.username, request.password)
    if not user:
        write_audit_entry(
            user=request.username,
            role=request.role,
            action="login",
            policy_decision="deny",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Reject if the role in the request doesn't match the stored role
    if user["role"] != request.role:
        write_audit_entry(
            user=request.username,
            role=request.role,
            action="login",
            policy_decision="deny",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User '{request.username}' does not have role '{request.role}'",
        )

    token = create_access_token({"sub": user["username"], "role": user["role"]})
    write_audit_entry(
        user=user["username"],
        role=user["role"],
        action="login",
        policy_decision="allow",
    )
    return TokenResponse(access_token=token)
