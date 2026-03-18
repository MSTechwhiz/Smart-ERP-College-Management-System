# Smart College ERP System - Product Requirements Document

## Original Problem Statement
Build a comprehensive Smart College ERP System with:
- FastAPI backend with MongoDB
- Role-based dashboards (Principal, Admin, HOD, Faculty, Student)
- Complete CRUD operations for all entities
- Multi-step approval workflows (Grievances, Documents, Fees)
- Screenshot-based fee payment verification
- Settings with theme/password/notifications
- Audit logging for all actions

## Architecture

### Tech Stack
- **Backend**: FastAPI, Pydantic, Motor (async MongoDB), PyJWT
- **Frontend**: React, Vite, Tailwind CSS, shadcn/ui, Axios, React Router
- **Database**: MongoDB

### Project Structure
```
/app
├── backend/
│   ├── server.py          # Main FastAPI application (monolithic)
│   ├── auth.py            # JWT authentication
│   ├── models.py          # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── admin/AdminDashboard.js
│   │   │   ├── student/StudentDashboard.js
│   │   │   ├── hod/HODDashboard.js
│   │   │   ├── faculty/FacultyDashboard.js
│   │   │   └── principal/PrincipalDashboard.js
│   │   ├── components/ui/SettingsPage.jsx
│   │   └── services/api.js
│   └── package.json
└── memory/PRD.md
```

## What's Been Implemented (Feb 26, 2026)

### Global Features (All Dashboards)
- [x] Settings Page with shared component
  - Theme Mode (Light/Dark/System)
  - Color Scheme (Blue, Green, Purple, Orange, Red)
  - Password change functionality
  - Email/Push/SMS notification toggles
  - Account information display
  - Logout button
- [x] Role-based authentication with JWT
- [x] Demo credentials button on login
- [x] Real-time toast notifications

### Student Dashboard
- [x] Dashboard overview (CGPA, Attendance, Semester, Quick Actions)
- [x] Attendance tracking with percentage
- [x] Marks viewing with grades
- [x] CGPA calculation
- [x] **Fee Payment Flow** (NEW)
  - Bank Transfer Details display
  - UPI payment option with ID
  - QR Code placeholder
  - Screenshot URL upload
  - Transaction ID input
  - Submit for Verification button
- [x] **Document Request** (ENHANCED)
  - Multiple document types (Bonafide, TC, Marksheet, etc.)
  - Custom type option with text input
  - 5-step timeline tracking
  - Status badges
- [x] **Grievance Submission** (ENHANCED)
  - Category selection
  - Workflow path display
  - Timeline status tracking
  - Resolution viewing
- [x] Announcements viewing

### Admin Dashboard
- [x] Dashboard overview with stats
- [x] Students CRUD
- [x] Faculty CRUD
- [x] Departments management
- [x] Bulk Upload functionality
- [x] **Fee Management** (ENHANCED)
  - Fee Structures tab
  - **Pending Verification tab** (NEW)
  - Add Fee Structure dialog
  - Screenshot verification workflow
- [x] Document Requests verification
- [x] Grievance Management

### HOD Dashboard
- [x] Dashboard overview
- [x] Department students management
- [x] Department faculty management
- [x] Subjects management
- [x] Subject Mapping
- [x] Risk Alerts panel
- [x] **Approvals Page** (ENHANCED)
  - Document approval workflow
  - **Grievance handling** with:
    - Resolve option
    - Forward to Admin option
    - Add Comment option
  - Timeline and history tracking
- [x] Analytics

### Principal Dashboard
- [x] Institution-wide overview
- [x] Analytics dashboard
- [x] Approval center
- [x] Student overview with filters
- [x] Faculty overview

### Faculty Dashboard
- [x] Dashboard with assigned classes
- [x] Today's classes schedule
- [x] Attendance marking (bulk)
- [x] Marks entry (CIA, Model, Semester)
- [x] My Students list
- [x] My Subjects

## Backend API Endpoints

### Authentication
- POST /api/auth/login
- POST /api/auth/register
- GET /api/auth/me

### Fee Management
- GET /api/fees/structures
- POST /api/fees/structures
- POST /api/fees/initiate-manual-payment
- POST /api/fees/upload-screenshot/{payment_id}
- GET /api/fees/pending-verification
- PUT /api/fees/verify-screenshot/{payment_id}
- GET /api/fees/pending
- GET /api/fees/payments

### Grievances
- POST /api/grievances
- GET /api/grievances
- PUT /api/grievances/{id}/forward
- PUT /api/grievances/{id}/resolve
- POST /api/grievances/{id}/comment
- GET /api/grievances/{id}/comments

### Documents
- POST /api/documents/request
- GET /api/documents/requests
- PUT /api/documents/requests/{id}/verify
- PUT /api/documents/requests/{id}/approve
- PUT /api/documents/requests/{id}/sign
- PUT /api/documents/requests/{id}/reject

## Bug Fixes Applied (Feb 26, 2026)
- Fixed: SelectItem with empty string value causing React error
- Fixed: Settings page integration across all dashboards

## Test Credentials
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@academia.edu | admin123 |
| Student | student@academia.edu | student123 |
| HOD | hod.cse@academia.edu | hod123 |
| Faculty | faculty@academia.edu | faculty123 |
| Principal | principal@academia.edu | principal123 |

## Prioritized Backlog

### P0 (Critical)
- [ ] Refactor monolithic server.py into routers
- [ ] Add Razorpay integration for actual payments

### P1 (High)
- [ ] Add analytics charts (Recharts)
- [ ] Implement admission workflow UI
- [ ] Add export to PDF functionality

### P2 (Medium)
- [ ] Create pytest test suite
- [ ] Add bulk upload preview with validation
- [ ] Implement real-time notifications (WebSocket)

### P3 (Low)
- [ ] Add dark mode persistence
- [ ] Implement audit log viewer
- [ ] Add QR code generation for UPI

## Testing Status
- Backend: 100% pass rate
- Frontend: 95% pass rate (all features working)
- Last test: iteration_3 (Feb 26, 2026)
