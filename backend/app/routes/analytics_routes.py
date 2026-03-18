from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends
from ..core.security import require_roles
from ..services.analytics_service import AnalyticsService, get_analytics_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Analytics"])

@router.get("/analytics/dashboard", response_model=dict)
async def get_dashboard_analytics(
    user: dict = Depends(require_roles(["principal", "admin"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get overall institution analytics"""
    return await analytics_service.get_dashboard_analytics()

@router.get("/analytics/fees", response_model=dict)
async def get_fee_analytics(
    department_id: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "admin"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_fee_analytics(department_id)

@router.get("/analytics/attendance", response_model=dict)
async def get_attendance_analytics(
    department_id: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "hod", "admin"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_attendance_analytics(department_id, user["role"], user.get("department_id"))

@router.get("/analytics/risks", response_model=List[dict])
async def get_risk_analytics(
    department_id: Optional[str] = None,
    user: dict = Depends(require_roles(["principal", "hod", "admin"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_risk_analytics(department_id, user["role"], user.get("department_id"))
@router.get("/analytics/department/{department_id}", response_model=dict)
async def get_department_analytics(
    department_id: str,
    user: dict = Depends(require_roles(["principal", "hod", "admin"])),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    return await analytics_service.get_department_analytics(department_id)
