from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse
from ..core.security import get_current_user, require_roles
from ..services.upload_service import UploadService
from ..core.config import get_settings

router = APIRouter(prefix="/api/upload", tags=["Upload"])
service = UploadService()
settings = get_settings()

@router.post("/document/{student_id}", response_model=dict)
async def upload_student_document(
    student_id: str,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(require_roles(["admin", "principal", "faculty"]))
):
    doc = await service.upload_student_document(student_id, document_type, file, user)
    return {"message": "Document uploaded successfully", "document": doc}

@router.get("/files/{folder}/{filename}")
async def get_file(folder: str, filename: str, user: dict = Depends(get_current_user)):
    file_path = settings.uploads_dir / folder / filename
    if not file_path.exists():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@router.post("/students", response_model=dict)
async def upload_students_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user: dict = Depends(require_roles(["principal", "admin"]))
):
    return await service.upload_students_excel(file, user)

@router.post("/marks", response_model=dict)
async def upload_marks_excel(
    file: UploadFile = File(...),
    user: dict = Depends(require_roles(["faculty", "admin"]))
):
    return await service.upload_marks_excel(file, user)

@router.post("/attendance", response_model=dict)
async def upload_attendance_excel(
    file: UploadFile = File(...),
    user: dict = Depends(require_roles(["faculty", "admin"]))
):
    return await service.upload_attendance_excel(file, user)

