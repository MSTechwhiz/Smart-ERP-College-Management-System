from typing import List, Optional
from fastapi import APIRouter, Depends
from ..core.security import require_roles
from ..services.audit_service import AuditService

router = APIRouter(prefix="/api/audit-logs", tags=["Audit Logs"])
service = AuditService()

@router.get("", response_model=dict)
async def get_audit_logs_enhanced(
    module: Optional[str] = None,
    action: Optional[str] = None,
    role: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    skip: int = 0,
    user: dict = Depends(require_roles(["principal", "admin"]))
):
    return await service.get_audit_logs(
        module, action, role, start_date, end_date, limit, skip
    )

@router.get("/export")
async def export_audit_logs(
    module: Optional[str] = None,
    action: Optional[str] = None,
    role: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "admin"]))
):
    return await service.export_audit_logs(
        module, action, role, start_date, end_date
    )
