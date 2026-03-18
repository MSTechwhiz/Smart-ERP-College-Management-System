from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse
from ..core.security import get_current_user, require_roles
from ..schemas.document_schema import DocumentRequestCreate
from ..services.document_service import DocumentService

router = APIRouter(prefix="/api", tags=["Documents"])
service = DocumentService()

@router.post("/documents/request", response_model=dict)
async def create_document_request(
    request_data: DocumentRequestCreate,
    user: dict = Depends(require_roles(["student"]))
):
    doc = await service.create_document_request(request_data, user)
    return {"message": "Document request submitted", "request": doc}

@router.get("/documents/requests", response_model=List[dict])
async def get_document_requests(
    status: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    return await service.get_document_requests(user, status)

@router.put("/documents/requests/{request_id}/verify", response_model=dict)
async def verify_document_request(
    request_id: str,
    remarks: Optional[str] = None,
    user: dict = Depends(require_roles(["admin"]))
):
    return await service.update_workflow_status(
        request_id, user, "verified", "Verified", 
        next_level="office", remarks=remarks, required_level="office"
    )

@router.put("/documents/requests/{request_id}/forward", response_model=dict)
async def forward_document_request(
    request_id: str,
    remarks: Optional[str] = None,
    user: dict = Depends(require_roles(["admin"]))
):
    return await service.update_workflow_status(
        request_id, user, "forwarded", "Verified", 
        next_level="principal", remarks=remarks, required_level="office"
    )

@router.put("/documents/requests/{request_id}/approve", response_model=dict)
async def approve_document_request(
    request_id: str,
    remarks: Optional[str] = None,
    user: dict = Depends(require_roles(["principal"]))
):
    return await service.update_workflow_status(
        request_id, user, "approved", "Approved", 
        next_level="office", remarks=remarks, required_level="principal"
    )

@router.put("/documents/requests/{request_id}/sign", response_model=dict)
async def sign_document_request(
    request_id: str,
    remarks: Optional[str] = None,
    user: dict = Depends(require_roles(["admin"]))
):
    return await service.update_workflow_status(
        request_id, user, "signed", "Signed", 
        next_level="office", remarks=remarks, required_level="office"
    )

@router.put("/documents/requests/{request_id}/issue", response_model=dict)
async def issue_document_request(
    request_id: str,
    remarks: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    user: dict = Depends(require_roles(["admin"]))
):
    return await service.update_workflow_status(
        request_id, user, "issued", "Issued", 
        next_level="office", remarks=remarks, required_level="office",
        file=file
    )

@router.put("/documents/requests/{request_id}/reject", response_model=dict)
async def reject_document_request(
    request_id: str,
    remarks: str,
    user: dict = Depends(require_roles(["admin", "principal"]))
):
    return await service.update_workflow_status(
        request_id, user, "rejected", "Rejected", remarks=remarks
    )

@router.get("/documents/requests/{request_id}", response_model=dict)
async def get_document_request_detail(
    request_id: str,
    user: dict = Depends(get_current_user)
):
    return await service.get_document_detail(request_id, user)

@router.get("/documents/download/{request_id}")
async def download_document_file(
    request_id: str,
    user: dict = Depends(get_current_user)
):
    doc = await service.get_document_detail(request_id, user)
    if not doc.get("file_url"):
        raise HTTPException(status_code=404, detail="File not found or not yet issued")
    
    # Extract path from URL /api/upload/files/issued_documents/filename
    # settings.uploads_dir is BASE_DIR / uploads
    from ..core.config import get_settings
    settings = get_settings()
    
    path_parts = doc["file_url"].split("/")
    if len(path_parts) < 4:
        raise HTTPException(status_code=500, detail="Invalid file URL")
        
    folder = path_parts[-2]
    filename = path_parts[-1]
    
    file_path = settings.uploads_dir / folder / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
        
    return FileResponse(
        file_path, 
        filename=filename,
        media_type="application/pdf"
    )
