from fastapi import APIRouter, Depends

from app.audit import read_audit_entries
from app.rbac import require_role

router = APIRouter()


@router.get("/logs")
def get_audit_logs(user: dict = Depends(require_role("view_audit"))):
    return read_audit_entries()
