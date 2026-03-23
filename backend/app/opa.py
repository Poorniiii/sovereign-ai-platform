import httpx
from fastapi import HTTPException, status

from app.config import settings


def check_policy(role: str, action: str) -> bool:
    """
    Ask OPA whether the given role is allowed to perform action.
    Returns True if allowed, False if denied.
    Raises 503 if OPA is unreachable (fail closed — never fail open).
    """
    try:
        response = httpx.post(
            f"{settings.opa_url}/v1/data/sovereign/allow",
            json={"input": {"role": role, "action": action}},
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json().get("result", False)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Policy engine timed out",
        )
    except httpx.HTTPError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Policy engine unreachable",
        )
