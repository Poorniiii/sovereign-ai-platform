import uuid

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.audit import write_audit_entry
from app.config import settings
from app.rbac import require_role

router = APIRouter()


class WorkflowRequest(BaseModel):
    query: str
    file_content: str = ""
    workflow_id: str = ""


@router.post("/trigger")
def trigger_workflow(
    request: WorkflowRequest,
    user: dict = Depends(require_role("run_agent")),
):
    workflow_id = request.workflow_id or f"WF-{uuid.uuid4().hex[:8].upper()}"

    # Write audit entry for the trigger action
    write_audit_entry(
        user=user["sub"],
        role=user["role"],
        action="run_agent",
        policy_decision="allow",
        workflow_id=workflow_id,
    )

    # Call the LangGraph worker
    try:
        response = httpx.post(
            f"{settings.langgraph_url}/run",
            json={
                "query": request.query,
                "file_content": request.file_content,
                "workflow_id": workflow_id,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        result = response.json()
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LangGraph worker timed out",
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LangGraph worker error: {str(e)}",
        )

    # Update audit entry with agent output
    write_audit_entry(
        user=user["sub"],
        role=user["role"],
        action="run_agent",
        policy_decision="allow",
        workflow_id=workflow_id,
        agent_output=result.get("verdict", ""),
    )

    return {
        "workflow_id": workflow_id,
        "status": result.get("status", "completed"),
        "verdict": result.get("verdict"),
        "confidence": result.get("confidence"),
        "answer": result.get("answer"),
    }
