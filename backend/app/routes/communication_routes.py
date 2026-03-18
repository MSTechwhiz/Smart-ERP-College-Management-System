from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from ..core.security import get_current_user, require_roles
from ..schemas.communication_schema import CommunicationCreate, CommunicationResponse, Communication
from ..services.communication_service import CommunicationService, get_communication_service

router = APIRouter(prefix="/api/communications", tags=["Communications"])

@router.post("/send", response_model=dict)
async def send_communication(
    comm_data: CommunicationCreate,
    user: dict = Depends(get_current_user), # Role checking is handled in the service
    comm_service: CommunicationService = Depends(get_communication_service)
):
    """Send a new internal communication to a specific role."""
    doc = await comm_service.send_communication(comm_data, user)
    return {"message": "Communication sent successfully", "communication": doc}

@router.get("/inbox", response_model=List[CommunicationResponse])
async def get_my_inbox(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(get_current_user),
    comm_service: CommunicationService = Depends(get_communication_service)
):
    """Retrieve all internal communications targeting the current user's role."""
    return await comm_service.get_my_inbox(user, skip, limit)

@router.get("/sent", response_model=List[CommunicationResponse])
async def get_my_sent(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: dict = Depends(require_roles(["admin", "principal", "hod", "faculty"])),
    comm_service: CommunicationService = Depends(get_communication_service)
):
    """Retrieve all internal communications sent by the current user."""
    return await comm_service.get_my_sent(user, skip, limit)

@router.get("/{comm_id}", response_model=CommunicationResponse)
async def get_communication(
    comm_id: str,
    user: dict = Depends(get_current_user),
    comm_service: CommunicationService = Depends(get_communication_service)
):
    """Retrieve a specific communication details. Will mark as read if viewed by recipient."""
    return await comm_service.get_communication_by_id(comm_id, user)
    
@router.delete("/{comm_id}", response_model=dict)
async def delete_communication(
    comm_id: str,
    user: dict = Depends(get_current_user),
    comm_service: CommunicationService = Depends(get_communication_service)
):
    """Soft delete a sent communication."""
    await comm_service.delete_communication(comm_id, user)
    return {"message": "Communication deleted successfully"}
