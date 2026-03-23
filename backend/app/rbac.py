from fastapi import Depends, HTTPException, status

from app.audit import write_audit_entry
from app.dependencies import get_current_user
from app.opa import check_policy


def require_role(action: str):
    """
    FastAPI dependency factory.
    Usage: Depends(require_role("run_agent"))
    Checks JWT identity then asks OPA if the role can perform the action.
    Writes an audit entry for both allow and deny outcomes so every
    authorization decision is recorded, including 403s that never reach
    the route body.
    Raises 403 if OPA denies.
    """
    def dependency(user: dict = Depends(get_current_user)) -> dict:
        allowed = check_policy(role=user["role"], action=action)
        if not allowed:
            write_audit_entry(
                user=user["sub"],
                role=user["role"],
                action=action,
                policy_decision="deny",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{user['role']}' is not permitted to perform '{action}'",
            )
        write_audit_entry(
            user=user["sub"],
            role=user["role"],
            action=action,
            policy_decision="allow",
        )
        return user

    return dependency
