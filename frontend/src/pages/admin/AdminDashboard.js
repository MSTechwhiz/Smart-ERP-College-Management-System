import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  Upload,
  FileSpreadsheet,
  DollarSign,
  Settings,
  ClipboardList,
  Building2,
  UserPlus,
  FileText,
  AlertTriangle,
  Trash2,
  Eye,
  Megaphone,
  History,
  Info,
  ChevronDown,
  Bell,
  MessageSquare,
  Activity,
  Search,
  Plus,
  Pencil,
  Power,
  PowerOff,
  Loader2,
  Download,
  User,
  CheckCircle2
} from 'lucide-react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { useAuth } from '../../context/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Textarea } from '../../components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import { EnhancedStudentForm } from '../../components/ui/EnhancedStudentForm';
import { AuditLogs } from '../../components/ui/AuditLogs';
import { DepartmentDetails } from '../../components/ui/DepartmentDetails';
import StudentDetailsPage from './StudentDetailsPage';
import { Communications } from '../shared/Communications';
import {
  studentAPI,
  facultyAPI,
  departmentAPI,
  uploadAPI,
  feeAPI,
  documentAPI,
  grievanceAPI,
  analyticsAPI,
  announcementAPI,
  enhancedStudentAPI
} from '../../services/api';
import { toast } from 'sonner';
import { cn, formatCurrency, formatDateTime, getStatusColor, getYearLabel } from '../../lib/utils';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/admin' },
  { icon: GraduationCap, label: 'Students', href: '/admin/students' },
  { icon: Users, label: 'Faculty', href: '/admin/faculty' },
  { icon: Building2, label: 'Departments', href: '/admin/departments' },
  { icon: Upload, label: 'Bulk Upload', href: '/admin/upload' },
  { icon: DollarSign, label: 'Fee Management', href: '/admin/fees' },
  { icon: FileText, label: 'Document Requests', href: '/admin/documents' },
  { icon: AlertTriangle, label: 'Grievances', href: '/admin/grievances' },
  { icon: Bell, label: 'Announcements', href: '/admin/announcements' },
  { icon: MessageSquare, label: 'Communications', href: '/admin/communications' },
  { icon: Activity, label: 'Audit Logs', href: '/admin/audit' },
  { icon: Settings, label: 'Settings', href: '/admin/settings' },
];

// Dashboard Overview
function DashboardOverview() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ students: 0, faculty: 0, departments: 0, pendingDocs: 0, openGrievances: 0 });
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [studentsRes, facultyRes, deptRes, docsRes, grievancesRes, annRes] = await Promise.all([
        studentAPI.getAll(),
        facultyAPI.getAll(),
        departmentAPI.getAll(),
        documentAPI.getAll(),
        grievanceAPI.getAll(),
        announcementAPI.getAll().catch(() => ({ data: [] }))
      ]);
      setStats({
        students: studentsRes.data.total,
        faculty: facultyRes.data.length,
        departments: deptRes.data.length,
        pendingDocs: docsRes.data.filter(d => d.status === 'Pending').length,
        openGrievances: grievancesRes.data.filter(g => g.status === 'open').length
      });
      setAnnouncements(annRes.data.slice(0, 3));
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/students')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Students</p>
                <p className="text-3xl font-bold mono">{stats.students}</p>
              </div>
              <GraduationCap className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/faculty')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Faculty</p>
                <p className="text-3xl font-bold mono">{stats.faculty}</p>
              </div>
              <Users className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/departments')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Departments</p>
                <p className="text-3xl font-bold mono">{stats.departments}</p>
              </div>
              <Building2 className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/documents')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Docs</p>
                <p className="text-3xl font-bold mono">{stats.pendingDocs}</p>
              </div>
              <FileText className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/grievances')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Open Grievances</p>
                <p className="text-3xl font-bold mono">{stats.openGrievances}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="quick-add-student" onClick={() => navigate('/admin/students')}>
              <UserPlus className="h-5 w-5" />
              <span>Add Student</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="quick-add-faculty" onClick={() => navigate('/admin/faculty')}>
              <Users className="h-5 w-5" />
              <span>Add Faculty</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="quick-bulk-upload" onClick={() => navigate('/admin/upload')}>
              <Upload className="h-5 w-5" />
              <span>Bulk Upload</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="quick-fee-config" onClick={() => navigate('/admin/fees')}>
              <DollarSign className="h-5 w-5" />
              <span>Fee Config</span>
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground text-center py-4">
              Recent admin activities will appear here
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Announcements */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle>Recent Announcements</CardTitle>
          <Megaphone className="h-5 w-5 text-primary" />
        </CardHeader>
        <CardContent>
          {announcements.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">No recent announcements</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {announcements.map((ann) => (
                <div
                  key={ann.id}
                  className="p-4 rounded-lg bg-muted/30 border border-muted hover:border-primary/50 transition-colors cursor-pointer"
                  onClick={() => navigate('/admin/announcements')}
                >
                  <div className="flex justify-between items-start mb-2">
                    <Badge variant="outline" className="text-[10px]">{ann.type}</Badge>
                    <span className="text-[10px] text-muted-foreground">{formatDateTime(ann.publish_date)}</span>
                  </div>
                  <h4 className="font-semibold text-sm mb-1 line-clamp-1">{ann.title}</h4>
                  <p className="text-xs text-muted-foreground line-clamp-2">{ann.content}</p>
                </div>
              ))}
            </div>
          )}
          {announcements.length > 0 && (
            <div className="text-center mt-4">
              <Button
                variant="link"
                size="sm"
                onClick={() => navigate('/admin/announcements')}
              >
                View All Announcements
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Students Page with full CRUD
function StudentsPage() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showEnhancedForm, setShowEnhancedForm] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [viewStudent, setViewStudent] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('all');
  const [selectedYear, setSelectedYear] = useState('all');
  const [selectedQuota, setSelectedQuota] = useState('all');
  
  const normalizeQuota = (value) => {
    if (!value) return "";
    const val = value.toUpperCase();
    if (val.includes("MQ") || val.includes("MANAGEMENT")) return "Management Quota";
    if (val.includes("7.5")) return "7.5 Quota";
    if (val.includes("PMSS") || val.includes("PMMS")) return "PMSS";
    if (val.includes("FG") || val.includes("GF")) return "FG Quota";
    if (val.includes("GQ") || val.includes("GOVERNMENT") || val.includes("COUNSELLING")) return "Government Quota";
    return value;
  };

  // Debounced search term
  const [debouncedSearch, setDebouncedSearch] = useState('');

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchTerm), 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch, selectedDept, selectedYear, selectedQuota]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {
        search: debouncedSearch || undefined,
        department_id: selectedDept !== 'all' ? selectedDept : undefined,
        year: selectedYear !== 'all' ? parseInt(selectedYear) : undefined,
        category: selectedQuota !== 'all' ? selectedQuota : undefined,
        limit: 100 // We can increase this or add pagination later
      };

      const [studentsRes, deptRes] = await Promise.all([
        studentAPI.getAll(params),
        departmentAPI.getAll()
      ]);
      setStudents(studentsRes.data.students);
      setDepartments(deptRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (studentId) => {
    if (!window.confirm('Are you sure you want to delete this student?')) return;
    try {
      await studentAPI.delete(studentId);
      toast.success('Student deleted successfully');
      setStudents(prev => prev.filter(s => s.id !== studentId));
    } catch (error) {
      // toast is handled by interceptor
    }
  };

  const handleToggleStatus = async (student) => {
    try {
      await studentAPI.update(student.id, { is_active: !student.is_active });
      toast.success(`Student ${!student.is_active ? 'activated' : 'deactivated'} successfully`);
      setStudents(prev => prev.map(s => s.id === student.id ? { ...s, is_active: !s.is_active } : s));
    } catch (error) {
      toast.error('Failed to update student status');
    }
  };

  const handleEditStudent = async (student) => {
    try {
      setLoading(true);
      const response = await enhancedStudentAPI.getProfile(student.id);
      // Ensure the student and user info are merged for the form
      const fullStudent = {
        ...response.data.student,
        name: response.data.user.name,
        email: response.data.user.email
      };
      setEditingStudent(fullStudent);
      setShowEnhancedForm(true);
    } catch (error) {
      toast.error('Failed to load student details for editing');
    } finally {
      setLoading(false);
    }
  };

  const getDepartmentName = (deptId) => {
    const dept = departments.find(d => d.id === deptId);
    return dept ? dept.name : 'Unknown';
  };

  if (loading && !students.length) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Student Records</h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search students..."
              className="pl-9 w-64"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Select value={selectedDept} onValueChange={setSelectedDept}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Departments" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {departments.map((dept) => (
                <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={selectedYear} onValueChange={setSelectedYear}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="All Years" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Years</SelectItem>
              <SelectItem value="1">1st Year</SelectItem>
              <SelectItem value="2">2nd Year</SelectItem>
              <SelectItem value="3">3rd Year</SelectItem>
              <SelectItem value="4">Final Year</SelectItem>
            </SelectContent>
          </Select>
          <Select value={selectedQuota} onValueChange={setSelectedQuota}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="Admission Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="Government Quota">Government Quota</SelectItem>
              <SelectItem value="Management Quota">Management Quota</SelectItem>
              <SelectItem value="7.5 Quota">7.5 Quota</SelectItem>
              <SelectItem value="PMSS">PMSS</SelectItem>
              <SelectItem value="FG Quota">FG Quota</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={() => setShowEnhancedForm(true)} data-testid="add-student-btn">
            <UserPlus className="h-4 w-4 mr-2" />
            Add Student
          </Button>
        </div>
      </div>

      {/* Enhanced Student Form Dialog */}
      {showEnhancedForm && <EnhancedStudentForm
        isOpen={showEnhancedForm}
        onClose={() => { setShowEnhancedForm(false); setEditingStudent(null); }}
        onSuccess={() => { loadData(); }}
        editStudent={editingStudent}
      />}

      {/* View Student Dialog */}
      <Dialog open={!!viewStudent} onOpenChange={() => setViewStudent(null)}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Student Details</DialogTitle>
          </DialogHeader>
          {viewStudent && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 border-b pb-4">
                <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center text-primary text-xl font-bold">
                  {viewStudent.name.charAt(0)}
                </div>
                <div>
                  <h3 className="text-xl font-bold">{viewStudent.name}</h3>
                  <p className="text-muted-foreground">{viewStudent.email} • {getDepartmentName(viewStudent.department_id)}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Email</p>
                    <p className="font-medium">{viewStudent.email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Roll Number</p>
                    <p className="font-medium mono">{viewStudent.roll_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Reg Number</p>
                    <p className="font-medium mono">{viewStudent.register_number || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Department</p>
                    <p className="font-medium">{getDepartmentName(viewStudent.department_id)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Batch</p>
                    <p className="font-medium">{viewStudent.batch}</p>
                  </div>
                   <div>
                     <p className="text-sm text-muted-foreground">Year / Semester</p>
                     <p className="font-medium">{getYearLabel(viewStudent.semester)} / Sem {viewStudent.semester}</p>
                   </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Section</p>
                    <p className="font-medium">{viewStudent.section || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">CGPA</p>
                    <p className="font-medium">{viewStudent.cgpa?.toFixed(2) || 'N/A'}</p>
                  </div>
                </div>

              {/* Enhanced Data Sections */}
              {viewStudent.parent_details && (
                <div>
                  <h4 className="font-medium mb-3 text-primary">Parent Details</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Father's Name</p>
                      <p className="font-medium">{viewStudent.parent_details.father_name || '-'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Mother's Name</p>
                      <p className="font-medium">{viewStudent.parent_details.mother_name || '-'}</p>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button variant="outline" onClick={() => setViewStudent(null)}>Close</Button>
                <Button onClick={() => navigate(`/admin/student/${viewStudent.id}`)}>View Full Profile</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Card>
        <CardContent className="pt-6">
          {students.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No students found matching your criteria.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Roll No</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Email</th>
                    <th className="text-left py-3 px-4 font-medium">Batch</th>
                    <th className="text-left py-3 px-4 font-medium">Status</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {students
                    .filter(student => {
                      if (selectedQuota === 'all') return true;
                      return normalizeQuota(student.admission_quota) === selectedQuota;
                    })
                    .map((student) => (
                    <tr key={student.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 mono text-xs text-muted-foreground">{student.roll_number}</td>
                      <td className="py-3 px-4">
                        <div className="font-medium">{student.name}</div>
                        <div className="text-xs text-muted-foreground">{student.register_number}</div>
                      </td>
                      <td className="py-3 px-4 text-muted-foreground">{student.email}</td>
                      <td className="py-3 px-4">
                         <div>{getYearLabel(student.semester)} (Sem {student.semester})</div>
                         <div className="text-[10px] text-muted-foreground italic">{student.batch}</div>
                         <div className="text-[10px] text-primary font-medium">{normalizeQuota(student.admission_quota)}</div>
                       </td>
                      <td className="py-3 px-4">
                        <Badge variant={student.is_active !== false ? 'default' : 'secondary'}>
                          {student.is_active !== false ? 'Active' : 'Inactive'}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-1">
                          <Button variant="ghost" size="icon" onClick={() => setViewStudent(student)} title="Quick View">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" className="text-primary" onClick={() => handleEditStudent(student)} title="Edit">
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleToggleStatus(student)}
                            title={student.is_active !== false ? "Deactivate" : "Activate"}
                          >
                            {student.is_active !== false ? <PowerOff className="h-4 w-4 text-orange-600" /> : <Power className="h-4 w-4 text-emerald-600" />}
                          </Button>
                          <Button variant="ghost" size="icon" className="text-destructive" onClick={() => handleDelete(student.id)} title="Delete">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Faculty Page with full CRUD
function FacultyPage() {
  const [faculty, setFaculty] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [viewFaculty, setViewFaculty] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDept, setSelectedDept] = useState('all');
  const [formData, setFormData] = useState({
    email: '', name: '', password: '', employee_id: '',
    department_id: '', designation: '', specialization: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [facultyRes, deptRes] = await Promise.all([
        facultyAPI.getAll(),
        departmentAPI.getAll()
      ]);
      setFaculty(facultyRes.data);
      setDepartments(deptRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      email: '', name: '', password: '', employee_id: '',
      department_id: '', designation: '', specialization: ''
    });
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await facultyAPI.create(formData);
      toast.success('Faculty created successfully');
      setDialogOpen(false);
      resetForm();
      loadData();
    } catch (error) {
      // toast is handled by interceptor
    }
  };

  const handleDelete = async (facultyId) => {
    if (!window.confirm('Are you sure you want to delete this faculty member?')) return;
    try {
      await facultyAPI.delete(facultyId);
      toast.success('Faculty deleted successfully');
      loadData();
    } catch (error) {
      // toast is handled by interceptor
    }
  };

  const getDepartmentName = (deptId) => {
    const dept = departments.find(d => d.id === deptId);
    return dept ? dept.name : 'Unknown';
  };

  const filteredFaculty = faculty.filter(f => {
    const searchLower = searchTerm.toLowerCase();
    const matchesSearch = f.name?.toLowerCase().includes(searchLower) || 
                          f.email?.toLowerCase().includes(searchLower) ||
                          f.employee_id?.toLowerCase().includes(searchLower);
    const matchesDept = selectedDept === 'all' || f.department_id === selectedDept;
    return matchesSearch && matchesDept;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Faculty Records</h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search faculty..."
              className="pl-9 w-64"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <Select value={selectedDept} onValueChange={setSelectedDept}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Departments" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Departments</SelectItem>
              {departments.map((dept) => (
                <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Dialog open={dialogOpen} onOpenChange={(open) => { setDialogOpen(open); if (!open) resetForm(); }}>
            <DialogTrigger asChild>
              <Button data-testid="add-faculty-btn">
                <UserPlus className="h-4 w-4 mr-2" />
                Add Faculty
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Add New Faculty</DialogTitle>
                <DialogDescription>Enter faculty details below</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreate} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Name</Label>
                    <Input
                      data-testid="faculty-name-input"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input
                      type="email"
                      data-testid="faculty-email-input"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Employee ID</Label>
                    <Input
                      data-testid="faculty-empid-input"
                      value={formData.employee_id}
                      onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Password</Label>
                    <Input
                      type="password"
                      data-testid="faculty-password-input"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Department</Label>
                  <Select
                    value={formData.department_id}
                    onValueChange={(value) => setFormData({ ...formData, department_id: value })}
                  >
                    <SelectTrigger data-testid="faculty-dept-select">
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      {departments.map((dept) => (
                        <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Designation</Label>
                    <Select
                      value={formData.designation}
                      onValueChange={(value) => setFormData({ ...formData, designation: value })}
                    >
                      <SelectTrigger data-testid="faculty-designation-select">
                        <SelectValue placeholder="Select designation" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Professor">Professor</SelectItem>
                        <SelectItem value="Associate Professor">Associate Professor</SelectItem>
                        <SelectItem value="Assistant Professor">Assistant Professor</SelectItem>
                        <SelectItem value="Lecturer">Lecturer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Specialization</Label>
                    <Input
                      data-testid="faculty-spec-input"
                      value={formData.specialization}
                      onChange={(e) => setFormData({ ...formData, specialization: e.target.value })}
                      placeholder="e.g., AI/ML"
                    />
                  </div>
                </div>
                <Button type="submit" className="w-full" data-testid="submit-faculty-btn">Create Faculty</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Dialog open={!!viewFaculty} onOpenChange={() => setViewFaculty(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Faculty Details</DialogTitle>
          </DialogHeader>
          {viewFaculty && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Name</p>
                  <p className="font-medium">{viewFaculty.name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="font-medium">{viewFaculty.email}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Employee ID</p>
                  <p className="font-medium mono">{viewFaculty.employee_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Department</p>
                  <p className="font-medium">{getDepartmentName(viewFaculty.department_id)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Designation</p>
                  <p className="font-medium">{viewFaculty.designation}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Specialization</p>
                  <p className="font-medium">{viewFaculty.specialization || '-'}</p>
                </div>
              </div>
              {viewFaculty.is_class_incharge && (
                <Badge className="mt-2">Class Incharge: {viewFaculty.incharge_class}</Badge>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Card>
        <CardContent className="pt-6">
          {filteredFaculty.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No faculty found matching your criteria.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Employee ID</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Email</th>
                    <th className="text-left py-3 px-4 font-medium">Department</th>
                    <th className="text-left py-3 px-4 font-medium">Designation</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredFaculty.map((fac) => (
                    <tr key={fac.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 mono">{fac.employee_id}</td>
                      <td className="py-3 px-4 font-medium">{fac.name}</td>
                      <td className="py-3 px-4 text-muted-foreground">{fac.email}</td>
                      <td className="py-3 px-4">{getDepartmentName(fac.department_id)}</td>
                      <td className="py-3 px-4">{fac.designation}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2">
                          <Button variant="ghost" size="sm" onClick={() => setViewFaculty(fac)} data-testid={`view-faculty-${fac.id}`}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm" className="text-destructive" onClick={() => handleDelete(fac.id)} data-testid={`delete-faculty-${fac.id}`}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Departments Page with CRUD
function DepartmentsPage() {
  const navigate = useNavigate();
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({ name: '', code: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await departmentAPI.getAll();
      setDepartments(response.data);
    } catch (error) {
      toast.error('Failed to load departments');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await departmentAPI.create(formData);
      toast.success('Department created successfully');
      setDialogOpen(false);
      setFormData({ name: '', code: '' });
      loadData();
    } catch (error) {
      // toast is handled by interceptor
    }
  };

  const handleDelete = async (deptId) => {
    if (!window.confirm('Are you sure you want to delete this department?')) return;
    try {
      await departmentAPI.delete(deptId);
      toast.success('Department deleted successfully');
      loadData();
    } catch (error) {
      // toast is handled by interceptor
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Department Setup</h2>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-dept-btn">
              <Plus className="h-4 w-4 mr-2" />
              Add Department
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-sm" aria-describedby={undefined}>
            <DialogHeader>
              <DialogTitle>Add New Department</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Department Name</Label>
                <Input
                  data-testid="dept-name-input"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Computer Science"
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Department Code</Label>
                <Input
                  data-testid="dept-code-input"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                  placeholder="e.g., CSE"
                  required
                />
              </div>
              <Button type="submit" className="w-full" data-testid="submit-dept-btn">Create Department</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="py-8 text-center text-muted-foreground">
              No departments found. Click "Add Department" to create one.
            </CardContent>
          </Card>
        ) : (
          departments.map((dept) => (
            <Card
              key={dept.id}
              className="card-interactive cursor-pointer group hover:border-primary transition-all"
              onClick={(e) => {
                if (e.target.closest('.delete-btn')) return;
                navigate(`/admin/department/${dept.id}`);
              }}
            >
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="h-12 w-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center group-hover:bg-primary/10 transition-colors">
                    <Building2 className="h-6 w-6 text-purple-600 group-hover:text-primary" />
                  </div>
                  <Badge variant="outline" className="mono">{dept.code}</Badge>
                </div>
                <h3 className="font-semibold mb-2">{dept.name}</h3>
                <div className="flex justify-end">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(dept.id);
                    }}
                    data-testid={`delete-dept-${dept.id}`}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Bulk Upload Page
function BulkUploadPage() {
  const [uploading, setUploading] = useState(false);
  const [selectedType, setSelectedType] = useState('students');
  const [result, setResult] = useState(null);

  const handleDownloadTemplate = () => {
    let headers = [];
    let fileName = '';

    if (selectedType === 'students') {
      headers = [
        'email', 'name', 'password', 'registration_number', 'department_code', 
        'batch', 'semester', 'section', 'student_mobile', 'parent_name', 
        'parent_contact', 'address'
      ];
      fileName = 'student_upload_template.xlsx';
    } else if (selectedType === 'marks') {
      headers = ['registration_number', 'subject_code', 'academic_year', 'semester', 'exam_type', 'marks'];
      fileName = 'marks_upload_template.xlsx';
    } else if (selectedType === 'attendance') {
      headers = ['registration_number', 'subject_code', 'date', 'status'];
      fileName = 'attendance_upload_template.xlsx';
    }

    // Create CSV content with BOM to ensure Excel partitions columns correctly
    const csvContent = '\uFEFF' + headers.join(',') + '\n';
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setResult(null);

    try {
      let response;
      switch (selectedType) {
        case 'students':
          response = await uploadAPI.students(file);
          break;
        case 'marks':
          response = await uploadAPI.marks(file);
          break;
        case 'attendance':
          response = await uploadAPI.attendance(file);
          break;
        default:
          throw new Error('Invalid upload type');
      }
      setResult(response.data);
      toast.success(response.data.message);
    } catch (error) {
      // toast is handled by interceptor
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Bulk Data Upload</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Upload Excel File</CardTitle>
            <CardDescription>
              Upload Excel files to bulk import data into the system
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Data Type</Label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger data-testid="upload-type-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="students">Students</SelectItem>
                  <SelectItem value="marks">Marks</SelectItem>
                  <SelectItem value="attendance">Attendance</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Excel File</Label>
              <Input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleUpload}
                disabled={uploading}
                data-testid="upload-file-input"
              />
            </div>

            {uploading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                Processing...
              </div>
            )}

            {result && (
              <div className="p-4 rounded-lg bg-muted">
                <p className="font-medium mb-2">{result.message}</p>
                {result.errors?.length > 0 && (
                  <div className="mt-2 space-y-1">
                    <p className="text-sm text-destructive">Errors:</p>
                    {result.errors.slice(0, 5).map((err, idx) => (
                      <p key={idx} className="text-xs text-muted-foreground">
                        Row {err.row}: {err.error}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle>Template Format</CardTitle>
              <CardDescription>
                Required columns for each data type
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleDownloadTemplate} className="text-primary border-primary hover:bg-primary/5">
              <Download className="h-4 w-4 mr-2" />
              Download Excel Template
            </Button>
          </CardHeader>
          <CardContent>
            {selectedType === 'students' && (
              <div className="space-y-2">
                <p className="font-medium text-sm text-primary">Student Upload Columns:</p>
                <div className="grid grid-cols-2 gap-x-4">
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>email (required)</li>
                    <li>name (required)</li>
                    <li>password (required)</li>
                    <li>registration_number (required)</li>
                    <li>department_code (required)</li>
                    <li>batch (required)</li>
                  </ul>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>semester (optional)</li>
                    <li>section (optional)</li>
                    <li>student_mobile (required)</li>
                    <li>parent_name (required)</li>
                    <li>parent_contact (required)</li>
                    <li>address (optional)</li>
                  </ul>
                </div>
              </div>
            )}
            {selectedType === 'marks' && (
              <div className="space-y-2">
                <p className="font-medium text-sm">Marks Upload Columns:</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>registration_number (required)</li>
                  <li>subject_code (required)</li>
                  <li>academic_year (required)</li>
                  <li>semester (required)</li>
                  <li>exam_type (required)</li>
                  <li>marks (required)</li>
                </ul>
              </div>
            )}
            {selectedType === 'attendance' && (
              <div className="space-y-2">
                <p className="font-medium text-sm">Attendance Upload Columns:</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>registration_number (required)</li>
                  <li>subject_code (required)</li>
                  <li>date (required, YYYY-MM-DD)</li>
                  <li>status (required: present/absent/od)</li>
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// Fee Management Page
function FeesPage() {
  const [feeStructures, setFeeStructures] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [pendingVerification, setPendingVerification] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('structures');
  const [notificationHistory, setNotificationHistory] = useState([]);
  const [reminderResults, setReminderResults] = useState(null);
  const [runningReminders, setRunningReminders] = useState(false);
  const [formData, setFormData] = useState({
    name: '', category: 'tuition', amount: '', department_id: '', batch: '', semester: '', due_date: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [feesRes, deptRes, pendingRes, historyRes] = await Promise.all([
        feeAPI.getStructures({ all: true }),
        departmentAPI.getAll(),
        feeAPI.getPendingVerification(),
        feeAPI.getNotificationHistory().catch(() => ({ data: [] }))
      ]);
      setFeeStructures(feesRes.data);
      setDepartments(deptRes.data);
      setPendingVerification(pendingRes.data || []);
      setNotificationHistory(historyRes.data || []);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleRunReminders = async () => {
    setRunningReminders(true);
    try {
      const response = await feeAPI.sendReminders();
      setReminderResults(response.data);
      toast.success(response.data.message);
      loadData(); // Refresh history
    } catch (error) {
      // toast.error is handled by interceptor
    } finally {
      setRunningReminders(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      if (formData.id) {
        await feeAPI.updateStructure(formData.id, {
          ...formData,
          amount: parseFloat(formData.amount),
          semester: formData.semester ? parseInt(formData.semester) : null
        });
        toast.success('Fee structure updated successfully');
      } else {
        await feeAPI.createStructure({
          ...formData,
          amount: parseFloat(formData.amount),
          semester: formData.semester ? parseInt(formData.semester) : null
        });
        toast.success('Fee structure created successfully');
      }
      setDialogOpen(false);
      setFormData({ name: '', category: 'tuition', amount: '', department_id: '', batch: '', semester: '', due_date: '' });
      loadData();
    } catch (error) {
      // toast is handled by interceptor
    }
  };

  const handleDeactivate = async (feeId, currentStatus) => {
    try {
      await feeAPI.updateStructure(feeId, { is_active: !currentStatus });
      toast.success(`Fee structure ${!currentStatus ? 'activated' : 'deactivated'} successfully`);
      loadData();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  const handleDelete = async (feeId) => {
    if (!window.confirm('Are you sure you want to delete this fee structure? This will only work if no payments are linked.')) return;
    try {
      await feeAPI.deleteStructure(feeId);
      toast.success('Fee structure deleted successfully');
      setFeeStructures(prev => prev.filter(fee => fee.id !== feeId));
    } catch (error) {
      // toast is handled by interceptor
    }
  };


  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Fee Management</h2>
        <div className="flex items-center gap-4">
          {/* Tab Buttons */}
          <div className="flex rounded-lg bg-muted p-1">
            <Button
              variant={activeTab === 'structures' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('structures')}
              data-testid="fee-structures-tab"
            >
              Fee Structures
            </Button>
            <Button
              variant={activeTab === 'verification' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('verification')}
              data-testid="verification-tab"
            >
              Fee Tracking
              {pendingVerification.length > 0 && (
                <Badge variant="destructive" className="ml-2">{pendingVerification.length}</Badge>
              )}
            </Button>
            <Button
              variant={activeTab === 'history' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('history')}
              data-testid="notification-history-tab"
            >
              Notification History
            </Button>
          </div>
          <Button 
            variant="outline" 
            onClick={handleRunReminders} 
            disabled={runningReminders}
            className="border-primary text-primary hover:bg-primary/5"
          >
            {runningReminders ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Bell className="h-4 w-4 mr-2" />
            )}
            Run Fee Notification
          </Button>
          {activeTab === 'structures' && (
            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button data-testid="add-fee-btn" onClick={() => setFormData({ name: '', category: 'tuition', amount: '', department_id: '', batch: '', semester: '', due_date: '' })}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Fee Structure
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-md" aria-describedby={undefined}>
                <DialogHeader>
                  <DialogTitle>{formData.id ? 'Edit Fee Structure' : 'Create Fee Structure'}</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreate} className="space-y-4">
                  <div className="space-y-2">
                    <Label>Fee Name</Label>
                    <Input
                      data-testid="fee-name-input"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="e.g., Semester Fee - Sem 5"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Category</Label>
                      <Select value={formData.category} onValueChange={(v) => setFormData({ ...formData, category: v })}>
                        <SelectTrigger data-testid="fee-category-select">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="tuition">Tuition</SelectItem>
                          <SelectItem value="exam">Exam</SelectItem>
                          <SelectItem value="semester">Semester</SelectItem>
                          <SelectItem value="transport">Transport</SelectItem>
                          <SelectItem value="hostel">Hostel</SelectItem>
                          <SelectItem value="misc">Miscellaneous</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Amount (INR)</Label>
                      <Input
                        type="number"
                        data-testid="fee-amount-input"
                        value={formData.amount}
                        onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                        placeholder="50000"
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Department (Optional)</Label>
                    <Select value={formData.department_id || "all"} onValueChange={(v) => setFormData({ ...formData, department_id: v === "all" ? "" : v })}>
                      <SelectTrigger>
                        <SelectValue placeholder="All departments" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Departments</SelectItem>
                        {departments.map((dept) => (
                          <SelectItem key={dept.id} value={dept.id}>{dept.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Batch (Optional)</Label>
                      <Input
                        value={formData.batch}
                        onChange={(e) => setFormData({ ...formData, batch: e.target.value })}
                        placeholder="2024-2028"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Due Date</Label>
                      <Input
                        type="date"
                        value={formData.due_date}
                        onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                      />
                    </div>
                  </div>
                  <Button type="submit" className="w-full" data-testid="submit-fee-btn">
                    {formData.id ? 'Update Fee Structure' : 'Create Fee Structure'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>


      {/* Reminder Results Dialog */}
      <Dialog open={!!reminderResults} onOpenChange={() => setReminderResults(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Notification Sent Successfully</DialogTitle>
            {reminderResults?.demo_email_sent ? (
              <CardDescription>Demo email sent to one student for live demonstration.</CardDescription>
            ) : (
              <CardDescription>The following students received reminders:</CardDescription>
            )}
          </DialogHeader>
          <>
          
          {reminderResults?.demo_email_sent && (
            <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200 flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                <Megaphone className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm font-bold text-blue-900 line-height-tight">Demo Email Delivered</p>
                <p className="text-xs text-blue-700">{reminderResults.demo_recipient}</p>
              </div>
            </div>
          )}

          <div className="max-h-60 overflow-y-auto space-y-2 mt-4">
            {reminderResults?.notified_students?.length === 0 ? (
              <p className="text-center text-muted-foreground py-4 italic">No other students matched the due dates within 2 days.</p>
            ) : (
                reminderResults?.notified_students?.map((s, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-emerald-50 border border-emerald-100">
                  <div>
                    <p className="font-bold text-sm">{s.student_name} – {s.mobile || 'No Mobile'}</p>
                    <p className="text-[10px] text-muted-foreground mono">{s.roll_number}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold font-mono text-sm text-emerald-700">{formatCurrency(s.amount)}</p>
                    <p className={`text-[10px] font-bold ${s.status.includes('Delivered') || s.status.includes('Sent') ? 'text-emerald-600' : 'text-orange-600'}`}>
                      {s.status}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
            <Button onClick={() => setReminderResults(null)} className="w-full mt-4">Close</Button>
          </>
        </DialogContent>
      </Dialog>

      {/* Tab Content */}
      {activeTab === 'structures' ? (
        <Card>
          <CardContent className="pt-6">
            {feeStructures.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No fee structures found. Click "Add Fee Structure" to create one.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium">Name</th>
                      <th className="text-left py-3 px-4 font-medium">Category</th>
                      <th className="text-left py-3 px-4 font-medium">Amount</th>
                      <th className="text-left py-3 px-4 font-medium">Due Date</th>
                      <th className="text-left py-3 px-4 font-medium">Status</th>
                      <th className="text-right py-3 px-4 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feeStructures.map((fee) => (
                      <tr key={fee.id} className="border-b hover:bg-muted/50">
                        <td className="py-3 px-4 font-medium">{fee.name}</td>
                        <td className="py-3 px-4 capitalize">{fee.category}</td>
                        <td className="py-3 px-4 mono">{formatCurrency(fee.amount)}</td>
                        <td className="py-3 px-4">{fee.due_date || '-'}</td>
                        <td className="py-3 px-4">
                          <Badge variant={fee.is_active ? 'default' : 'secondary'} className={fee.is_active ? 'bg-emerald-100 text-emerald-700' : ''}>
                            {fee.is_active ? 'Active' : 'Inactive'}
                          </Badge>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => {
                                setFormData({
                                  id: fee.id,
                                  name: fee.name,
                                  category: fee.category,
                                  amount: fee.amount.toString(),
                                  department_id: fee.department_id || '',
                                  batch: fee.batch || '',
                                  semester: fee.semester?.toString() || '',
                                  due_date: fee.due_date || ''
                                });
                                setDialogOpen(true);
                              }}
                              title="Edit"
                            >
                              <Pencil className="h-4 w-4 text-blue-600" />
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDeactivate(fee.id, fee.is_active)}
                              title={fee.is_active ? "Deactivate" : "Activate"}
                            >
                              {fee.is_active ? <PowerOff className="h-4 w-4 text-orange-600" /> : <Power className="h-4 w-4 text-emerald-600" />}
                            </Button>
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              onClick={() => handleDelete(fee.id)}
                              title="Delete"
                            >
                              <Trash2 className="h-4 w-4 text-rose-600" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      ) : activeTab === 'verification' ? (
        <Card>
          <CardHeader>
            <CardTitle>Fee Tracking System</CardTitle>
            
          </CardHeader>
          <CardContent>
            {pendingVerification.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center border rounded-xl bg-muted/10">
                <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center mb-4">
                  <CheckCircle2 className="h-6 w-6 text-muted-foreground" />
                </div>
                <h3 className="text-lg font-semibold">No Pending Fees</h3>
                <p className="text-sm text-muted-foreground">All students have cleared their current fee structures.</p>
              </div>
            ) : (
              <div className="border rounded-xl overflow-hidden bg-background shadow-sm">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-muted/50 border-b">
                      <th className="text-left p-4 font-bold text-[11px] uppercase tracking-wider text-muted-foreground">Student Details</th>
                      <th className="text-left p-4 font-bold text-[11px] uppercase tracking-wider text-muted-foreground">Department</th>
                      <th className="text-right p-4 font-bold text-[11px] uppercase tracking-wider text-muted-foreground">Total Fee</th>
                      <th className="text-right p-4 font-bold text-[11px] uppercase tracking-wider text-muted-foreground">Paid Fees</th>
                      <th className="text-right p-4 font-bold text-[11px] uppercase tracking-wider text-muted-foreground">Pending Fees</th>
                      <th className="text-center p-4 font-bold text-[11px] uppercase tracking-wider text-muted-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {pendingVerification.map((student) => (
                      <tr key={student.id} className="hover:bg-muted/30 transition-colors">
                        <td className="p-4">
                          <div className="flex flex-col">
                            <span className="font-bold text-sm">{student.student_name}</span>
                            <span className="text-[10px] text-muted-foreground mono">{student.register_number}</span>
                          </div>
                        </td>
                        <td className="p-4 text-muted-foreground font-medium">{student.department_name}</td>
                        <td className="p-4 text-right font-bold mono">{formatCurrency(student.total_fee)}</td>
                        <td className="p-4 text-right font-bold mono text-emerald-600">{formatCurrency(student.paid_fees)}</td>
                        <td className="p-4 text-right font-bold mono text-rose-600">{formatCurrency(student.pending_fees)}</td>
                        <td className="p-4 text-center">
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-8 w-8 p-0"
                            onClick={() => window.open(`/admin/students/${student.id}`, '_blank')}
                            title="View Student Profile"
                          >
                            <User className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle>Notification History</CardTitle>
            <CardDescription>Log of simulated SMS and Flash fee reminders</CardDescription>
          </CardHeader>
          <CardContent>
            {notificationHistory.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No notification history available</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-muted-foreground">
                      <th className="text-left font-medium py-2">Date</th>
                      <th className="text-left font-medium py-2">Student</th>
                      <th className="text-left font-medium py-2">Fee Name</th>
                      <th className="text-right font-medium py-2">Amount</th>
                      <th className="text-center font-medium py-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {notificationHistory.map((log) => (
                      <tr key={log.id} className="border-b hover:bg-muted/50">
                        <td className="py-3 px-1 text-xs text-muted-foreground">{formatDateTime(log.created_at)}</td>
                        <td className="py-3 px-1">
                          <p className="font-medium">{log.student_name}</p>
                          <p className="text-[10px] text-muted-foreground">{log.mobile_number || 'No Mobile'}</p>
                        </td>
                        <td className="py-3 px-1">{log.fee_name}</td>
                        <td className="py-3 px-1 text-right font-bold mono">{formatCurrency(log.amount)}</td>
                        <td className="py-3 px-1 text-center">
                          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-100 uppercase text-[10px]">{log.status}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div >
  );
}

// Document Requests Page
function DocumentRequestsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [file, setFile] = useState(null);
  const [remarks, setRemarks] = useState('');
  const [issuing, setIssuing] = useState(false);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      const response = await documentAPI.getAll();
      setRequests(response.data);
    } catch (error) {
      toast.error('Failed to load document requests');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (requestId, action, label) => {
    try {
      if (action === 'verify') await documentAPI.verify(requestId);
      else if (action === 'forward') await documentAPI.forward(requestId);
      else if (action === 'sign') await documentAPI.sign(requestId);
      else if (action === 'issue') await documentAPI.issue(requestId);

      toast.success(`Document ${label} successfully`);
      loadRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || `Failed to ${action}`);
    }
  };

  const handleReject = async (requestId) => {
    const rejectionRemarks = prompt("Enter rejection reason:");
    if (!rejectionRemarks) return;
    try {
      await documentAPI.reject(requestId, rejectionRemarks);
      toast.success('Request rejected');
      loadRequests();
    } catch (error) {
      toast.error('Failed to reject request');
    }
  };

  const handleIssueWithFile = async () => {
    if (!file && selectedRequest?.delivery_type === 'soft') {
      toast.error('Please select a file to upload');
      return;
    }

    setIssuing(true);
    try {
      await documentAPI.issue(selectedRequest.id, remarks, file);
      toast.success('Document issued successfully');
      setSelectedRequest(null);
      setFile(null);
      setRemarks('');
      loadRequests();
    } catch (error) {
      // toast.error is handled by interceptor
    } finally {
      setIssuing(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Document Requests</h2>

      <Card>
        <CardContent className="pt-6">
          {requests.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No document requests</p>
          ) : (
            <div className="space-y-4">
              {requests.map((req) => (
                <div key={req.id} className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium">{req.student_name}</span>
                      <span className="text-sm text-muted-foreground">({req.roll_number})</span>
                    </div>
                    <p className="text-sm capitalize font-semibold">{req.document_type.replace('_', ' ')}</p>
                    <Badge className={`mt-2 ${getStatusColor(req.status)}`}>
                      {req.status}
                    </Badge>
                  </div>
                  <div className="flex gap-2">
                    {req.status === 'Pending' && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => handleAction(req.id, 'verify', 'Verified')} data-testid={`verify-${req.id}`}>
                          Verify Request
                        </Button>
                        <Button variant="destructive" size="sm" onClick={() => handleReject(req.id)}>
                          Reject
                        </Button>
                      </>
                    )}
                    {req.status === 'Verified' && req.current_level === 'office' && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => handleAction(req.id, 'forward', 'Forwarded to Principal')} className="text-blue-600 border-blue-600 hover:bg-blue-50">
                          Forward to Principal
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => handleAction(req.id, 'sign', 'Signed')} className="text-emerald-600 border-emerald-600 hover:bg-emerald-50">
                          Sign & Stamp
                        </Button>
                      </>
                    )}
                    {req.status === 'Approved' && (
                      <Button variant="outline" size="sm" onClick={() => handleAction(req.id, 'sign', 'Signed')} className="text-emerald-600 border-emerald-600 hover:bg-emerald-50">
                        Sign & Stamp
                      </Button>
                    )}
                    {req.status === 'Signed' && (
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={() => {
                          if (req.delivery_type === 'soft') {
                            setSelectedRequest(req);
                          } else {
                            handleAction(req.id, 'issue', 'Issued');
                          }
                        }} 
                        className="text-purple-600 border-purple-600 hover:bg-purple-50"
                      >
                        Issue Document
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Issuance Dialog for Soft Copies */}
      <Dialog open={!!selectedRequest} onOpenChange={(open) => { if (!open) setSelectedRequest(null); }}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Issue Soft Copy</DialogTitle>
            <CardDescription>
              Upload the document for {selectedRequest?.student_name}
            </CardDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Select Document (PDF)</Label>
              <Input 
                type="file" 
                accept=".pdf" 
                onChange={(e) => setFile(e.target.files[0])}
                data-testid="document-file-input"
              />
            </div>
            <div className="space-y-2">
              <Label>Remarks (Optional)</Label>
              <Textarea 
                value={remarks}
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Enter any instructions for the student..."
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedRequest(null)}>Cancel</Button>
            <Button onClick={handleIssueWithFile} disabled={issuing}>
              {issuing ? 'Uploading...' : 'Upload & Issue'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Grievances Page for Admin
function GrievancesPage() {
  const [grievances, setGrievances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGrievance, setSelectedGrievance] = useState(null);
  const [resolution, setResolution] = useState('');
  const [remarks, setRemarks] = useState('');
  const [actionType, setActionType] = useState(null); // 'resolve' or 'escalate'

  useEffect(() => {
    loadGrievances();
  }, []);

  const loadGrievances = async () => {
    try {
      const response = await grievanceAPI.getAll({
        current_level: 'admin'
      });
      setGrievances(response.data);
    } catch (error) {
      toast.error('Failed to load grievances');
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async () => {
    if (!resolution.trim()) {
      toast.error('Please enter a resolution');
      return;
    }
    try {
      await grievanceAPI.resolve(selectedGrievance.id, resolution);
      toast.success('Grievance resolved');
      setSelectedGrievance(null);
      setResolution('');
      loadGrievances();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to resolve grievance');
    }
  };

  const handleEscalate = async () => {
    try {
      await grievanceAPI.forward(selectedGrievance.id, 'principal', remarks);
      toast.success('Grievance escalated to Principal');
      setSelectedGrievance(null);
      setRemarks('');
      loadGrievances();
    } catch (error) {
      toast.error('Failed to escalate grievance');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this grievance?')) return;
    try {
      await grievanceAPI.delete(id);
      toast.success('Grievance deleted');
      loadGrievances();
    } catch (error) {
      toast.error('Failed to delete grievance');
    }
  };

  const getGrievanceStatusColor = (status) => {
    switch (status) {
      case 'open': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      case 'in_progress': return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
      case 'resolved': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'escalated': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
      default: return '';
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Grievance Management</h2>

      {/* Resolve Dialog */}
      <Dialog open={!!selectedGrievance} onOpenChange={() => { setSelectedGrievance(null); setResolution(''); }}>
        <DialogContent className="max-w-md" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Resolve Grievance</DialogTitle>
          </DialogHeader>
          {selectedGrievance && (
            <div className="space-y-4">
              <div>
                <p className="font-medium">{selectedGrievance.subject}</p>
                <p className="text-sm text-muted-foreground mt-1">{selectedGrievance.description}</p>
              </div>

              <div className="flex gap-4">
                <Button
                  variant={actionType === 'resolve' ? 'default' : 'outline'}
                  className="flex-1"
                  onClick={() => setActionType('resolve')}
                >
                  Resolve
                </Button>
                <Button
                  variant={actionType === 'escalate' ? 'destructive' : 'outline'}
                  className="flex-1"
                  onClick={() => setActionType('escalate')}
                >
                  Escalate to Principal
                </Button>
              </div>

              {actionType === 'resolve' && (
                <div className="space-y-2">
                  <Label>Resolution</Label>
                  <Textarea
                    value={resolution}
                    onChange={(e) => setResolution(e.target.value)}
                    placeholder="Enter resolution details..."
                    rows={4}
                  />
                  <Button onClick={handleResolve} className="w-full">
                    Mark as Resolved
                  </Button>
                </div>
              )}

              {actionType === 'escalate' && (
                <div className="space-y-2">
                  <Label>Remarks for Principal</Label>
                  <Textarea
                    value={remarks}
                    onChange={(e) => setRemarks(e.target.value)}
                    placeholder="Why are you escalating this?"
                    rows={2}
                  />
                  <Button onClick={handleEscalate} className="w-full" variant="destructive">
                    Confirm Escalation
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Card>
        <CardContent className="pt-6">
          {grievances.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No grievances found</p>
          ) : (
            <div className="space-y-4">
              {grievances.map((grievance) => (
                <div key={grievance.id} className="p-4 rounded-lg border">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-medium">{grievance.subject}</h4>
                      <p className="text-sm text-muted-foreground capitalize">{grievance.category}</p>
                    </div>
                    <Badge className={getGrievanceStatusColor(grievance.status)}>
                      {grievance.status.replace('_', ' ')}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{grievance.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      {formatDateTime(grievance.created_at)}
                    </span>
                    <div className="flex items-center gap-2">
                      <Button size="sm" onClick={() => {
                        setSelectedGrievance(grievance);
                        setActionType(null);
                      }} data-testid={`action-grievance-${grievance.id}`}>
                        Action
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-destructive"
                        onClick={() => handleDelete(grievance.id)}
                        data-testid={`delete-grievance-${grievance.id}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

import AnnouncementsPage from '../common/AnnouncementsPage';

// Settings Page - Use Shared Component
import { SettingsPage as SharedSettingsPage, ProfilePage } from '../../components/ui/SettingsPage';

function SettingsPageWrapper() {
  return <SharedSettingsPage />;
}

function ProfilePageWrapper() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await facultyAPI.getMyProfile(); // Admin is also a user
        setProfile(response.data);
      } catch (error) {
        console.error('Error loading profile:', error);
      } finally {
        setLoading(false);
      }
    };
    loadProfile();
  }, []);

  return <ProfilePage profile={profile} loading={loading} />;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  return (
    <DashboardLayout sidebarItems={sidebarItems} title="Admin Dashboard">
      <Routes>
        <Route index element={<DashboardOverview />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="faculty" element={<FacultyPage />} />
        <Route path="departments" element={<DepartmentsPage />} />
        <Route path="upload" element={<BulkUploadPage />} />
        <Route path="fees" element={<FeesPage />} />
        <Route path="documents" element={<DocumentRequestsPage />} />
        <Route path="grievances" element={<GrievancesPage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="communications" element={<Communications userRole="admin" userId={user?.id} />} />
        <Route path="audit" element={<AuditLogs />} />
        <Route path="settings" element={<SettingsPageWrapper />} />
        <Route path="profile" element={<ProfilePageWrapper />} />
        <Route path="student/:id" element={<StudentDetailsPage />} />
        <Route path="department/:id" element={<DepartmentDetails />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </DashboardLayout>
  );
}
