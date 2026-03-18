from typing import Any, Dict, List
from fastapi import Depends, HTTPException
from ..core.database import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas.communication_schema import CommunicationCreate, Communication
from ..repositories.communication_repository import CommunicationRepository, get_communication_repository
import uuid
from datetime import datetime, timezone

class CommunicationService:
    def __init__(self, comm_repo: CommunicationRepository):
        self.comm_repo = comm_repo

    def _can_send_to_role(self, sender_role: str, target_role: str) -> bool:
        """Define role-based permissions for sending communications"""
        allowed_targets = {
            "admin": ["principal", "hod", "faculty", "student"],
            "principal": ["hod", "faculty", "student"],
            "hod": ["faculty", "student"],
            "faculty": ["student"],
            "student": [] # Students cannot send messages via this module
        }
        return target_role in allowed_targets.get(sender_role, [])

    async def send_communication(self, comm_data: CommunicationCreate, sender: dict) -> Dict[str, Any]:
        """Process and send a new communication"""
        target_role = comm_data.target_role

        if not self._can_send_to_role(sender["role"], target_role):
            raise HTTPException(status_code=403, detail="You do not have permission to send communications to this role.")

        new_comm = Communication(
            title=comm_data.title,
            message=comm_data.message,
            target_role=target_role,
            priority=comm_data.priority,
            attachment_url=comm_data.attachment_url,
            sender_id=sender["id"],
            sender_role=sender["role"],
            sender_name=sender["name"]
        )

        return await self.comm_repo.create(new_comm.model_dump())

    async def get_my_inbox(self, user: dict, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve communications sent to the user's role"""
        user_role = user["role"]
        return await self.comm_repo.get_received_by_role(role=user_role, skip=skip, limit=limit)

    async def get_my_sent(self, user: dict, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve communications sent by this exact user"""
        return await self.comm_repo.get_sent_by_user(user_id=user["id"], skip=skip, limit=limit)
        
    async def get_communication_by_id(self, comm_id: str, user: dict) -> Dict[str, Any]:
        """Fetch a specific communication and verify access bounds"""
        comm = await self.comm_repo.get_by_id(comm_id)
        if not comm:
            raise HTTPException(status_code=404, detail="Communication not found")
            
        # Access control: user must be sender or the target role
        if comm["sender_id"] != user["id"] and comm["target_role"] != user["role"]:
            raise HTTPException(status_code=403, detail="Not authorized to view this communication")
            
        # Automatically mark as read if the current user is the recipient
        if comm["target_role"] == user["role"] and user["id"] not in comm["read_status"]:
            comm = await self.comm_repo.mark_as_read(comm_id, user["id"])
            
        return comm
        
    async def delete_communication(self, comm_id: str, user: dict) -> bool:
        """Deletes a communication, restricted to the sender or admin"""
        comm = await self.comm_repo.get_by_id(comm_id)
        if not comm:
            raise HTTPException(status_code=404, detail="Communication not found")
            
        if comm["sender_id"] != user["id"] and user["role"] != "admin":
             raise HTTPException(status_code=403, detail="Not authorized to delete this communication")
             
        return await self.comm_repo.delete(comm_id)


def get_communication_service(db: AsyncIOMotorDatabase = Depends(get_db)) -> CommunicationService:
    repo = get_communication_repository(db)
    return CommunicationService(repo)
