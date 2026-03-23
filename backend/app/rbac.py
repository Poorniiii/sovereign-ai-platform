from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.opa import check_policy


def require_role(action: str):
    """
    FastAPI dependency factory.
    Usage: Depends(require_role("run_agent"))
    Checks JWT identity then asks OPA if the role can perform the action.
    Raises 403 if OPA denies.
    """
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        allowed = check_policy(role=user["role"], action=action)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user['role']}' is not permitted to perform '{action}'",
            )
        return user

    return dependency
