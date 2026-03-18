from __future__ import annotations
from fastapi import APIRouter, Depends, BackgroundTasks
from ..core.security import require_roles
from ..core.automations import check_all_automations

router = APIRouter(prefix="/api/automation", tags=["Automation"])

@router.post("/trigger", response_model=dict)
async def trigger_automation(background_tasks: BackgroundTasks, user: dict = Depends(require_roles(["admin", "principal"]))):
    """Manually trigger all automation checks"""
    background_tasks.add_task(check_all_automations)
    return {"message": "Automation checks started in background"}
