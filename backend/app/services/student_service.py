from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid
import bcrypt
from fastapi import Depends, HTTPException

from ..repositories.student_repository import StudentRepository, get_student_repository
from ..repositories.user_repository import UserRepository, get_user_repository
from ..repositories.counter_repository import CounterRepository, get_counter_repository
from ..core.security import hash_password
from ..utils.auth_utils import generate_student_password
from ..core.audit import log_audit
from ..utils.cache import cache

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
import io


class StudentService:
    def __init__(self, student_repo: StudentRepository, user_repo: UserRepository, counter_repo: CounterRepository):
        self.student_repo = student_repo
        self.user_repo = user_repo
        self.counter_repo = counter_repo

    async def create_student(self, student_create_data: Any, admin_user_id: str) -> Dict[str, Any]:
        existing = await self.user_repo.get_by_email(student_create_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_id = str(uuid.uuid4())
        user_doc = {
            "id": user_id,
            "email": student_create_data.email,
            "name": student_create_data.name,
            "role": "student",
            "department_id": student_create_data.department_id,
            "password": await hash_password(generate_student_password(student_create_data.name)),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "permissions": [],
            "sub_roles": []
        }
        await self.user_repo.create(user_doc)

        roll_number = student_create_data.roll_number
        if not roll_number or not str(roll_number).strip():
            dept = await self.student_repo.get_department(student_create_data.department_id)
            dept_code = dept["code"] if dept else "UNK"
            batch = getattr(student_create_data, 'batch', '')
            batch_year = str(batch).split('-')[0] if '-' in str(batch) else str(datetime.now().year)
            year_short = batch_year[-2:]
            
            # ATOMIC ROLL NUMBER GENERATION
            counter_id = f"roll_seq_{dept_code}_{batch_year}"
            sequence = await self.counter_repo.get_next_sequence(counter_id)
            roll_number = f"{year_short}{dept_code}{str(sequence).zfill(3)}"
            
        existing_roll = await self.student_repo.get_by_roll_number(roll_number)
        if existing_roll:
            raise HTTPException(status_code=400, detail="Registration number already exists")

        student_id = str(uuid.uuid4())
        student_doc = {
            "id": student_id,
            "user_id": user_id,
            "roll_number": roll_number,
            "department_id": student_create_data.department_id,
            "batch": student_create_data.batch,
            "semester": student_create_data.semester,
            "section": student_create_data.section,
            "mentor_id": student_create_data.mentor_id,
            "regulation": student_create_data.regulation,
            "admission_date": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
            "cgpa": 0.0
        }
        await self.student_repo.create(student_doc)

        await log_audit(admin_user_id, "create", "student", student_id, after_value=student_doc)
        return student_doc

    async def get_students(self, query: Dict[str, Any], skip: int = 0, limit: Optional[int] = 100) -> Dict[str, Any]:
        # Clone query to avoid mutation issues
        repo_query = query.copy()
        
        # Normalization map (must match repository)
        if category := repo_query.get("admission_quota"):
            if isinstance(category, str):
                norm_map = {
                    "Management Quota": "(MQ|Management)",
                    "7.5 Quota": "7.5",
                    "PMSS": "(PMSS|PMMS)",
                    "FG Quota": "(FG|GF|F\\.G)",
                    "Government Quota": "(GQ|Government|COUNSELLING)"
                }
                if category in norm_map:
                    repo_query["admission_quota"] = {"$regex": norm_map[category], "$options": "i"}

        students = await self.student_repo.get_students_with_users(repo_query, skip=skip, limit=limit)
        
        # Calculate total count - if search is present, we need a lookup-aware count
        if "search" in repo_query:
            search_term = repo_query["search"]
            match_query = {k: v for k, v in repo_query.items() if k != "search"}
            pipeline = [
                {"$match": match_query},
                {"$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "id",
                    "as": "user_info"
                }},
                {"$unwind": "$user_info"},
                {"$match": {
                    "$or": [
                        {"user_info.name": {"$regex": search_term, "$options": "i"}},
                        {"user_info.email": {"$regex": search_term, "$options": "i"}},
                        {"roll_number": {"$regex": search_term, "$options": "i"}},
                        {"register_number": {"$regex": search_term, "$options": "i"}}
                    ]
                }},
                {"$count": "total"}
            ]
            count_res = await self.student_repo.collection.aggregate(pipeline).to_list(1)
            total = count_res[0]["total"] if count_res else 0
        else:
            total = await self.student_repo.collection.count_documents(repo_query)
            
        return {"students": students, "total": total}

    async def get_student(self, student_id: str) -> Optional[Dict[str, Any]]:
        return await self.student_repo.get_student_with_user(student_id)

    async def update_student(self, student_id: str, update_data: Dict[str, Any], admin_user_id: str) -> Dict[str, Any]:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        if update_data:
            await self.student_repo.update(student_id, update_data)
            
            # Synchronize is_active with User collection if present
            if "is_active" in update_data:
                await self.user_repo.update(student["user_id"], {"is_active": update_data["is_active"]})
                
            updated = await self.student_repo.get_by_id(student_id)
            # Invalidate cache
            await cache.delete(f"user_profile:{student['user_id']}")
            await cache.delete(f"user_permissions:{student['user_id']}")
            
            await log_audit(admin_user_id, "update", "student", student_id, before_value=student, after_value=updated)
            return updated
        return student

    async def delete_student(self, student_id: str, admin_user_id: str) -> bool:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        await self.user_repo.delete(student["user_id"])
        await self.student_repo.delete(student_id)
        
        # Invalidate cache
        await cache.delete(f"user_profile:{student['user_id']}")
        await cache.delete(f"user_permissions:{student['user_id']}")
        
        await log_audit(admin_user_id, "delete", "student", student_id, before_value=student)
        return True

    async def get_my_student_profile(self, user: dict) -> Dict[str, Any]:
        student = await self.student_repo.get_by_user_id(user["id"])
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        student["name"] = user["name"]
        student["email"] = user["email"]

        dept = await self.student_repo.get_department(student["department_id"])
        if dept:
            student["department_name"] = dept.get("name")
            student["department_code"] = dept.get("code")

        return student

    async def get_student_full_profile(self, student_id: str, user: dict) -> Dict[str, Any]:
        # RBAC check
        if user["role"] == "student":
            student = await self.student_repo.get_by_user_id(user["id"])
            if not student or student["id"] != student_id:
                raise HTTPException(status_code=403, detail="Access denied")
        elif user["role"] == "faculty":
            # Check if student is in faculty's assigned class
            faculty = await self.student_repo.get_faculty_by_user_id(user["id"])
            if faculty and faculty.get("is_class_incharge"):
                student = await self.student_repo.get_by_id(student_id)
                if not student:
                    raise HTTPException(status_code=404, detail="Student not found")
                # Allow if same department
                if student.get("department_id") != faculty.get("department_id"):
                    raise HTTPException(status_code=403, detail="Access denied - different department")
            else:
                raise HTTPException(status_code=403, detail="Access denied")
        elif user["role"] == "hod":
            student = await self.student_repo.get_by_id(student_id)
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")
            if student.get("department_id") != user.get("department_id"):
                raise HTTPException(status_code=403, detail="Access denied - different department")
        
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        user_info = await self.student_repo.get_user(student["user_id"])
        documents = await self.student_repo.get_documents(student_id)
        dept = await self.student_repo.get_department(student.get("department_id"))
        
        return {
            "student": student,
            "user": user_info,
            "documents": documents,
            "department_name": dept.get("name") if dept else None
        }

    async def get_student_documents(self, student_id: str, user: dict) -> List[Dict[str, Any]]:
        # RBAC check
        if user["role"] == "student":
            student = await self.student_repo.get_by_user_id(user["id"])
            if not student or student["id"] != student_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        return await self.student_repo.get_documents(student_id)

    async def create_enhanced_student(self, params: dict, admin_user: dict) -> Dict[str, Any]:
        # Check if email exists
        existing = await self.student_repo.get_user_by_email(params["email"])
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
            
        with open("d:\\college2-main\\backend\\debug_log.txt", "a") as f:
            f.write(f"CREATE PARAMS: {params}\n")
            
        primary_reg = params.get("register_number")
        manual_roll = params.get("roll_number")
        
        final_roll_number = None
        if primary_reg and str(primary_reg).strip():
            final_roll_number = str(primary_reg).strip()
        elif manual_roll and str(manual_roll).strip():
            final_roll_number = str(manual_roll).strip()
            
        if not final_roll_number:
            dept = await self.student_repo.get_department(params["department_id"])
            dept_code = dept["code"] if dept else "UNK"
            batch_year = str(params["batch"]).split('-')[0] if '-' in str(params["batch"]) else str(datetime.now().year)
            year_short = batch_year[-2:]
            count = await self.student_repo.count_students_in_batch(params["department_id"], batch_year)
            final_roll_number = f"{year_short}{dept_code}{str(count + 1).zfill(3)}"
            
        params["roll_number"] = final_roll_number

        # Check roll number
        existing_roll = await self.student_repo.get_by_roll_number(final_roll_number)
        if existing_roll:
            raise HTTPException(status_code=400, detail="Registration number already exists")
        
        user_id = str(uuid.uuid4())
        hashed_password = await hash_password(params["password"])
        
        user_doc = {
            "id": user_id,
            "email": params["email"],
            "name": params["name"],
            "password": await hash_password(generate_student_password(params["name"])),
            "role": "student",
            "department_id": params["department_id"],
            "permissions": [],
            "sub_roles": [],
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await self.student_repo.create_user(user_doc)
        
        student_id = str(uuid.uuid4())
        student_doc = {
            "id": student_id,
            "user_id": user_id,
            "roll_number": params["roll_number"],
            "register_number": params["register_number"],
            "department_id": params["department_id"],
            "batch": params["batch"],
            "year": params["year"],
            "semester": params["semester"],
            "section": params["section"],
            "date_of_birth": params["date_of_birth"],
            "gender": params["gender"],
            "blood_group": params["blood_group"],
            "mobile_number": params["mobile_number"],
            "alternate_mobile": params["alternate_mobile"],
            "program_type": params.get("program_type"),
            "program_duration": params.get("program_duration"),
            "email": params["email"],
            "permanent_address": params["permanent_address"],
            "communication_address": params["communication_address"],
            "tenth_certificate": {
                "school_name": params["tenth_school_name"],
                "board": params["tenth_board"],
                "year_of_passing": params["tenth_year"],
                "total_marks": params["tenth_total_marks"],
                "marks_obtained": params["tenth_marks_obtained"],
                "percentage": params["tenth_percentage"],
                "certificate_url": None
            } if params["tenth_school_name"] else None,
            "twelfth_certificate": {
                "school_name": params["twelfth_school_name"],
                "board": params["twelfth_board"],
                "year_of_passing": params["twelfth_year"],
                "total_marks": params["twelfth_total_marks"],
                "marks_obtained": params["twelfth_marks_obtained"],
                "percentage": params["twelfth_percentage"],
                "cutoff": params["twelfth_cutoff"],
                "certificate_url": None
            } if params["twelfth_school_name"] else None,
            "identity_proof": {
                "id_type": params["id_type"],
                "id_number": params["id_number"],
                "document_url": None
            } if params["id_type"] else None,
            "community": params["community"],
            "scholarship_details": params["scholarship_details"],
            "is_first_graduate": params["is_first_graduate"],
            "parent_details": {
                "father_name": params["father_name"],
                "father_occupation": params["father_occupation"],
                "father_contact": params["father_contact"],
                "mother_name": params["mother_name"],
                "mother_occupation": params["mother_occupation"],
                "mother_contact": params["mother_contact"],
                "guardian_name": params["guardian_name"],
                "guardian_contact": params["guardian_contact"]
            },
            "hostel_day_scholar": params["hostel_day_scholar"],
            "admission_type": params["admission_type"],
            "cgpa": 0.0,
            "regulation": params["regulation"],
            "mentor_id": params["mentor_id"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "created_by": admin_user["id"],
            "is_active": True
        }
        await self.student_repo.create(student_doc)
        
        await log_audit(admin_user["id"], "create", "student", student_id, None, {"roll_number": params["roll_number"], "name": params["name"]}, user_name=admin_user["name"], user_role=admin_user["role"], module="students")
        
        if "_id" in student_doc:
            del student_doc["_id"]
        return student_doc


    async def update_student_profile(self, student_id: str, fields_to_update: dict, is_first_graduate: Optional[bool], parent_updates: dict, admin_user: dict) -> Dict[str, Any]:
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        old_value = dict(student)
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        for key, value in fields_to_update.items():
            if value is not None:
                # Handle nested updates for certificates and identity
                if key in ["program_type", "program_duration"]:
                    update_data[key] = value
                elif key.startswith("tenth_"):
                    cert_key = key.replace("tenth_", "")
                    current_cert = student.get("tenth_certificate", {}) or {}
                    # Map route param names to schema names
                    field_map = {"school_name": "school_name", "board": "board", "year": "year_of_passing", 
                                "total_marks": "total_marks", "marks_obtained": "marks_obtained", "percentage": "percentage"}
                    db_field = field_map.get(cert_key, cert_key)
                    current_cert[db_field] = value
                    update_data["tenth_certificate"] = current_cert
                elif key.startswith("twelfth_"):
                    cert_key = key.replace("twelfth_", "")
                    current_cert = student.get("twelfth_certificate", {}) or {}
                    field_map = {"school_name": "school_name", "board": "board", "year": "year_of_passing", 
                                "total_marks": "total_marks", "marks_obtained": "marks_obtained", 
                                "percentage": "percentage", "cutoff": "cutoff"}
                    db_field = field_map.get(cert_key, cert_key)
                    current_cert[db_field] = value
                    update_data["twelfth_certificate"] = current_cert
                elif key.startswith("id_"):
                    id_key = key.replace("id_", "")
                    current_id = student.get("identity_proof", {}) or {}
                    db_field = "id_type" if id_key == "type" else "id_number"
                    current_id[db_field] = value
                    update_data["identity_proof"] = current_id
                else:
                    update_data[key] = value
        
        if is_first_graduate is not None:
            update_data["is_first_graduate"] = is_first_graduate
        
        if parent_updates:
            current_parent = student.get("parent_details", {}) or {}
            current_parent.update(parent_updates)
            update_data["parent_details"] = current_parent
        
        if update_data:
            await self.student_repo.update(student_id, update_data)
        
        updated = await self.student_repo.get_by_id(student_id)
        await log_audit(admin_user["id"], "update", "student", student_id, before_value=old_value, after_value=update_data, user_name=admin_user["name"], user_role=admin_user["role"], module="students")
        return updated

    async def get_admission_form_pdf(self, student_id: str, admin_user: dict) -> io.BytesIO:
        data = await self.get_student_full_profile(student_id, admin_user)
        student = data["student"]
        user = data["user"]
        dept_name = data["department_name"] or "N/A"
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, alignment=1, spaceAfter=20)
        section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=12, color=colors.HexColor("#1e293b"), spaceBefore=10, spaceAfter=10)
        label_style = ParagraphStyle('Label', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold')
        value_style = ParagraphStyle('Value', parent=styles['Normal'], fontSize=9)
        
        elements = []
        
        # Header
        elements.append(Paragraph("ACADEMIA UNIVERSITY", title_style))
        elements.append(Paragraph("OFFICIAL ADMISSION FORM", ParagraphStyle('SubTitle', parent=styles['Normal'], fontSize=10, alignment=1, spaceAfter=20)))
        
        # Basic Info Table
        elements.append(Paragraph("1. ADMISSION DETAILS", section_style))
        basic_data = [
            [Paragraph("Student Name", label_style), Paragraph(user.get("name", "N/A"), value_style), Paragraph("Roll Number", label_style), Paragraph(student.get("roll_number", "N/A"), value_style)],
            [Paragraph("Register No", label_style), Paragraph(student.get("register_number") or "N/A", value_style), Paragraph("Department", label_style), Paragraph(dept_name, value_style)],
            [Paragraph("Batch", label_style), Paragraph(student.get("batch", "N/A"), value_style), Paragraph("Admission Date", label_style), Paragraph(student.get("admission_date")[:10] if student.get("admission_date") else "N/A", value_style)],
            [Paragraph("Program Type", label_style), Paragraph(student.get("program_type", "N/A"), value_style), Paragraph("Regulation", label_style), Paragraph(student.get("regulation", "N/A"), value_style)]
        ]
        t = Table(basic_data, colWidths=[1.25*inch, 2*inch, 1.25*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t)
        
        # Personal Details
        elements.append(Paragraph("2. PERSONAL DETAILS", section_style))
        personal_data = [
            [Paragraph("Date of Birth", label_style), Paragraph(student.get("date_of_birth", "N/A"), value_style), Paragraph("Gender", label_style), Paragraph(student.get("gender", "N/A"), value_style)],
            [Paragraph("Blood Group", label_style), Paragraph(student.get("blood_group", "N/A"), value_style), Paragraph("Community", label_style), Paragraph(student.get("community", "N/A"), value_style)],
            [Paragraph("Mobile", label_style), Paragraph(student.get("mobile_number", "N/A"), value_style), Paragraph("Email", label_style), Paragraph(user.get("email", "N/A"), value_style)],
            [Paragraph("Address", label_style), Paragraph(student.get("permanent_address", "N/A"), value_style), "", ""]
        ]
        t2 = Table(personal_data, colWidths=[1.25*inch, 2*inch, 1.25*inch, 1.5*inch])
        t2.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('SPAN', (1,3), (3,3)),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t2)
        
        # Parent Details
        elements.append(Paragraph("3. FAMILY DETAILS", section_style))
        parents = student.get("parent_details", {}) or {}
        family_data = [
            [Paragraph("Father's Name", label_style), Paragraph(parents.get("father_name", "N/A"), value_style), Paragraph("Contact", label_style), Paragraph(parents.get("father_contact", "N/A"), value_style)],
            [Paragraph("Mother's Name", label_style), Paragraph(parents.get("mother_name", "N/A"), value_style), Paragraph("Contact", label_style), Paragraph(parents.get("mother_contact", "N/A"), value_style)]
        ]
        t3 = Table(family_data, colWidths=[1.25*inch, 2*inch, 1.25*inch, 1.5*inch])
        t3.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t3)
        
        # Academic Records
        elements.append(Paragraph("4. ACADEMIC QUALIFICATIONS", section_style))
        tenth = student.get("tenth_certificate") or {}
        twelfth = student.get("twelfth_certificate") or {}
        academic_data = [
            [Paragraph("Level", label_style), Paragraph("School/Board", label_style), Paragraph("Year", label_style), Paragraph("Percentage", label_style)],
            ["10th Standard", tenth.get("school_name", "N/A"), tenth.get("year_of_passing", "N/A"), f"{tenth.get('percentage', 'N/A')}%"],
            ["12th Standard", twelfth.get("school_name", "N/A"), twelfth.get("year_of_passing", "N/A"), f"{twelfth.get('percentage', 'N/A')}%"]
        ]
        t4 = Table(academic_data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1*inch])
        t4.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t4)
        
        # Declaration
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("DECLARATION", ParagraphStyle('Decl', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10)))
        elements.append(Paragraph("I hereby declare that all the information provided above is true to the best of my knowledge. I agree to abide by the rules and regulations of the institution.", styles['Normal']))
        
        # Signatures
        elements.append(Spacer(1, 1*inch))
        sig_data = [
            [Paragraph("_______________________", styles['Normal']), Paragraph("_______________________", styles['Normal'])],
            [Paragraph("Student Signature", styles['Normal']), Paragraph("Parent/Guardian Signature", styles['Normal'])]
        ]
        sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
        sig_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER')]))
        elements.append(sig_table)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer


def get_student_service(
    student_repo: StudentRepository = Depends(get_student_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    counter_repo: CounterRepository = Depends(get_counter_repository)
) -> StudentService:
    return StudentService(student_repo, user_repo, counter_repo)
