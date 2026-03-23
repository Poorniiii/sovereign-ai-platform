import logging

import httpx
from fastapi import HTTPException, status

from app.config import settings

logger = logging.getLogger(__name__)


def check_policy(role: str, action: str) -> bool:
    """
    Ask OPA whether the given role is allowed to perform action.
    Returns True if allowed, False if denied.
    Raises 503 if OPA is unreachable (fail closed — never fail open).

    OPA REST API contract for /v1/data/sovereign/allow:
      allowed  → {"result": true}
      denied   → {"result": false}
      undefined (no rule matched) → {}
    result is always a bool, never a nested object.
    """
    try:
        response = httpx.post(
            f"{settings.opa_url}/v1/data/sovereign/allow",
            json={"input": {"role": role, "action": action}},
            timeout=5.0,
        )
        response.raise_for_status()
        opa_response = response.json()

        if not isinstance(opa_response, dict):
            logger.error(
                "opa: unexpected response type %s: %r", type(opa_response).__name__, opa_response
            )
            return False  # fail closed

        result = opa_response.get("result")

        # Undefined rule → OPA returns {} with no "result" key → deny
        if result is None:
            return False

        if not isinstance(result, bool):
            logger.error(
                "opa: 'result' is %s, expected bool — response: %r",
                type(result).__name__,
                opa_response,
            )
            return False  # fail closed on unexpected shape

        return result
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
