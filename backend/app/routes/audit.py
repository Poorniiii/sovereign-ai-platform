from fastapi import APIRouter, Depends, Query

from app.audit import read_audit_entries_paginated
from app.rbac import require_role

router = APIRouter()


@router.get("/logs")
def get_audit_logs(
    user: dict = Depends(require_role("view_audit")),
    limit: int = Query(default=50, ge=1, le=500, description="Number of entries to return"),
    offset: int = Query(default=0, ge=0, description="Number of entries to skip"),
):
    return read_audit_entries_paginated(limit=limit, offset=offset)
