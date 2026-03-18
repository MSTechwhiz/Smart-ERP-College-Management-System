from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, UploadFile
from ..repositories.document_repository import DocumentRepository
from ..schemas.document_schema import DocumentRequestCreate, DocumentRequest
from .upload_service import UploadService
from ..websocket.manager import manager
from ..core.audit import log_audit

class DocumentService:
    def __init__(self):
        self.repo = DocumentRepository()
        self.upload_service = UploadService()

    async def create_document_request(self, request_data: DocumentRequestCreate, user: Dict[str, Any]) -> Dict[str, Any]:
        student = await self.repo.get_student_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        doc_request = DocumentRequest(
            student_id=student["id"],
            status="Pending",
            **request_data.model_dump()
        )
        
        initial_workflow = {
            "level": "student",
            "user_id": user["id"],
            "user_name": user["name"],
            "action": "submitted",
            "remarks": request_data.remarks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        doc_request.workflow_history = [initial_workflow]
        
        doc = doc_request.model_dump()
        doc["created_at"] = doc["created_at"].isoformat()
        doc["updated_at"] = doc["updated_at"].isoformat()
        
        created_doc = await self.repo.create_request(doc)
        await log_audit(user["id"], "create", "document_request", doc_request.id, None, created_doc)
        
        return created_doc

    async def get_document_requests(self, user: Dict[str, Any], status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = {}
        
        if user["role"] == "student":
            student = await self.repo.get_student_by_user_id(user["id"])
            if student:
                query["student_id"] = student["id"]
        elif user["role"] == "admin":
            if status:
                query["status"] = status
            else:
                query["current_level"] = "office"
        elif user["role"] == "principal":
            query["current_level"] = "principal"
            
        return await self.repo.get_requests_with_enrichment(query)

    async def update_workflow_status(
        self, 
        request_id: str, 
        user: Dict[str, Any], 
        action: str, 
        new_status: str, 
        next_level: Optional[str] = None, 
        remarks: Optional[str] = None,
        required_level: Optional[str] = None,
        file: Optional[UploadFile] = None
    ) -> Dict[str, Any]:
        doc_request = await self.repo.get_request_by_id(request_id)
        if not doc_request:
            raise HTTPException(status_code=404, detail="Request not found")
        
        if required_level and doc_request["current_level"] != required_level:
            raise HTTPException(status_code=400, detail=f"Request not at {required_level} level")
        
        workflow_entry = {
            "level": doc_request["current_level"],
            "user_id": user["id"],
            "user_name": user["name"],
            "action": action,
            "remarks": remarks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        update_data = {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if next_level:
            update_data["current_level"] = next_level
            
        if action == "rejected":
            update_data["remarks"] = remarks
            
        if action == "issued" and file:
            student = await self.repo.get_student_by_id(doc_request["student_id"])
            if student:
                roll_number = student.get("roll_number", "temp")
                file_url = await self.upload_service.upload_issued_document(
                    roll_number, doc_request["document_type"], file, user
                )
                update_data["file_url"] = file_url
            
        success = await self.repo.update_request(request_id, update_data, workflow_entry)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update request")
            
        # Notification logic
        if action in ["issued", "rejected"]:
            student = await self.repo.get_student_by_id(doc_request["student_id"])
            if student:
                notif_type = "document_ready" if action == "issued" else "document_rejected"
                notif_data = {"request_id": request_id, "document_type": doc_request["document_type"]}
                if action == "rejected":
                    notif_data["remarks"] = remarks
                    
                await manager.send_personal_message({
                    "type": notif_type,
                    "data": notif_data
                }, student["user_id"])
        
        await log_audit(user["id"], action, "document_request", request_id, None, {"status": new_status})
        
        return {"message": f"Document request {action} successfully", "status": new_status}

    async def get_document_detail(self, request_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        # Reuse get_requests_with_enrichment with a specific request_id to avoid duplication
        requests = await self.repo.get_requests_with_enrichment({"id": request_id})
        if not requests:
            raise HTTPException(status_code=404, detail="Request not found")
        
        doc_request = requests[0]
        
        # Verify access
        if user["role"] == "student":
            student = await self.repo.get_student_by_user_id(user["id"])
            if not student or student["id"] != doc_request["student_id"]:
                raise HTTPException(status_code=403, detail="Access denied")
                
        return doc_request
