import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Building2,
  GraduationCap,
  FileSpreadsheet,
  AlertTriangle,
  ClipboardList,
  Settings,
  TrendingUp,
  BarChart3,
  DollarSign,
  UserCheck,
  Search,
  CheckCircle2,
  Clock,
  ArrowRight,
  ChevronRight,
  Mail,
  Phone,
  Calendar,
  Megaphone,
  Plus,
  Eye,
  Trash2,
  FileCheck,
  History,
  MessageSquare
} from 'lucide-react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import { FeesAnalytics } from '../../components/ui/FeesAnalytics';
import { AuditLogs } from '../../components/ui/AuditLogs';
import { Communications } from '../shared/Communications';
import { analyticsAPI, auditAPI, grievanceAPI, announcementAPI, departmentAPI, studentAPI, facultyAPI, documentAPI } from '../../services/api';
import { toast } from 'sonner';
import { useAuth } from '../../context/AuthContext';
import { formatCurrency, formatDateTime, getRiskColor } from '../../lib/utils';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
} from 'recharts';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/principal' },
  { icon: Building2, label: 'Departments', href: '/principal/departments' },
  { icon: Users, label: 'Faculty', href: '/principal/faculty' },
  { icon: GraduationCap, label: 'Students', href: '/principal/students' },
  { icon: AlertTriangle, label: 'Risk Alerts', href: '/principal/risks' },
  { icon: MessageSquare, label: 'Grievances', href: '/principal/grievances' },
  { icon: FileCheck, label: 'Approvals', href: '/principal/approvals' },
  { icon: DollarSign, label: 'Fee Analytics', href: '/principal/fees' },
  { icon: ClipboardList, label: 'Audit Logs', href: '/principal/audit' },
  { icon: Megaphone, label: 'Announcements', href: '/principal/announcements' },
  { icon: MessageSquare, label: 'Communications', href: '/principal/communications' },
  { icon: Settings, label: 'Settings', href: '/principal/settings' },
];

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316'];

// Dashboard Overview Component
function DashboardOverview() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [recentAudit, setRecentAudit] = useState([]);
  const [announcements, setAnnouncements] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [analyticsRes, auditRes, annRes] = await Promise.all([
        analyticsAPI.getDashboard(),
        auditAPI.getAll({ limit: 5 }),
        announcementAPI.getAll().catch(() => ({ data: [] }))
      ]);
      setStats(analyticsRes.data);
      setRecentAudit(auditRes.data.logs || []);
      setAnnouncements(annRes.data.slice(0, 3));
    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const cgpaData = stats?.cgpa_distribution ?
    Object.entries(stats.cgpa_distribution).map(([grade, count]) => ({
      name: grade,
      value: count
    })) : [];

  const deptData = stats?.department_wise_students || [];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/principal/students')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Students</p>
                <p className="text-3xl font-bold mono">{stats?.total_students || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                <GraduationCap className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/principal/faculty')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Faculty</p>
                <p className="text-3xl font-bold mono">{stats?.total_faculty || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                <Users className="h-6 w-6 text-emerald-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/principal/departments')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Departments</p>
                <p className="text-3xl font-bold mono">{stats?.total_departments || 0}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                <Building2 className="h-6 w-6 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/principal/fees')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Fee Collected</p>
                <p className="text-2xl font-bold mono">{formatCurrency(stats?.total_fee_collected || 0)}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Department-wise Students */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-muted-foreground" />
              Department-wise Students
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="department" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* CGPA Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-muted-foreground" />
              CGPA Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={cgpaData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, value }) => `${name}: ${value}`}
                  >
                    {cgpaData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Announcements */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg flex items-center gap-2">
            <Megaphone className="h-5 w-5 text-primary" />
            Recent Announcements
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/principal/announcements')}
          >
            View All
          </Button>
        </CardHeader>
        <CardContent>
          {announcements.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-6">No recent announcements</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {announcements.map((ann) => (
                <div
                  key={ann.id}
                  className="p-4 rounded-lg bg-muted/30 border border-muted hover:border-primary/50 transition-colors cursor-pointer"
                  onClick={() => navigate('/principal/announcements')}
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
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <ClipboardList className="h-5 w-5 text-muted-foreground" />
            Recent Audit Activity
          </CardTitle>
          <CardDescription>Latest system changes and updates</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentAudit?.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No recent activity</p>
            ) : (
              recentAudit?.map((log, idx) => (
                <div key={idx} className="flex items-start gap-4 p-3 rounded-lg bg-muted/50">
                  <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <UserCheck className="h-4 w-4 text-primary" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">
                      <span className="text-primary">{log.user_name || 'System'}</span>
                      {' '}{log.action}{' '}
                      <span className="text-muted-foreground">{log.entity_type}</span>
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDateTime(log.timestamp)}
                    </p>
                  </div>
                  <Badge variant="outline" className="text-xs capitalize">
                    {log.action}
                  </Badge>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Departments Page with CRUD
function DepartmentsPage() {
  const navigate = useNavigate();
  const [departments, setDepartments] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [assignHodDialog, setAssignHodDialog] = useState(null);
  const [selectedHod, setSelectedHod] = useState('');
  const [formData, setFormData] = useState({ name: '', code: '' });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [deptRes, facultyRes] = await Promise.all([
        departmentAPI.getAll(),
        facultyAPI.getAll()
      ]);
      setDepartments(deptRes.data);
      setFaculty(facultyRes.data);
    } catch (error) {
      toast.error('Failed to load data');
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
      toast.error(error.response?.data?.detail || 'Failed to create department');
    }
  };

  const handleAssignHod = async () => {
    if (!selectedHod) {
      toast.error('Please select a faculty member');
      return;
    }
    try {
      await departmentAPI.update(assignHodDialog.id, { hod_id: selectedHod });
      toast.success('HOD assigned successfully');
      setAssignHodDialog(null);
      setSelectedHod('');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to assign HOD');
    }
  };

  const getHodName = (hodId) => {
    const hod = faculty.find(f => f.id === hodId);
    return hod ? hod.name : 'Not Assigned';
  };

  const getDeptFaculty = (deptId) => {
    return faculty.filter(f => f.department_id === deptId);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Departments</h2>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-department-btn">
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

      {/* Assign HOD Dialog */}
      <Dialog open={!!assignHodDialog} onOpenChange={() => { setAssignHodDialog(null); setSelectedHod(''); }}>
        <DialogContent className="max-w-sm" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Assign HOD</DialogTitle>
            <DialogDescription>
              Select a faculty member to assign as HOD for {assignHodDialog?.name}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Select value={selectedHod} onValueChange={setSelectedHod}>
              <SelectTrigger data-testid="hod-select">
                <SelectValue placeholder="Select faculty" />
              </SelectTrigger>
              <SelectContent>
                {assignHodDialog && getDeptFaculty(assignHodDialog.id).map((fac) => (
                  <SelectItem key={fac.id} value={fac.id}>
                    {fac.name} ({fac.employee_id})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleAssignHod} className="w-full" data-testid="submit-hod-btn">
              Assign HOD
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {departments.map((dept) => (
          <Card
            key={dept.id}
            className="card-interactive cursor-pointer group hover:border-primary transition-all"
            onClick={(e) => {
              if (e.target.closest('.action-btn')) return;
              navigate(`/principal/department/${dept.id}`);
            }}
          >
            <CardContent className="pt-6">
              <div className="flex items-start justify-between mb-4">
                <div className="h-12 w-12 rounded-xl bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center group-hover:bg-primary/10 transition-colors">
                  <Building2 className="h-6 w-6 text-blue-600 group-hover:text-primary" />
                </div>
                <Badge variant="outline" className="mono">{dept.code}</Badge>
              </div>
              <h3 className="font-semibold mb-1">{dept.name}</h3>
              <p className="text-sm text-muted-foreground mb-3">
                HOD: {dept.hod_id ? getHodName(dept.hod_id) : 'Not Assigned'}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="w-full action-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  setAssignHodDialog(dept);
                }}
                data-testid={`assign-hod-${dept.id}`}
              >
                {dept.hod_id ? 'Change HOD' : 'Assign HOD'}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

// Faculty Page
function FacultyPage() {
  const [faculty, setFaculty] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewFaculty, setViewFaculty] = useState(null);

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

  const getDepartmentName = (deptId) => {
    const dept = departments.find(d => d.id === deptId);
    return dept ? dept.name : 'Unknown';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Faculty Management</h2>

      {/* View Faculty Dialog */}
      <Dialog open={!!viewFaculty} onOpenChange={() => setViewFaculty(null)}>
        <DialogContent className="max-w-md" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Faculty Details</DialogTitle>
          </DialogHeader>
          {viewFaculty && (
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
          )}
        </DialogContent>
      </Dialog>

      <Card>
        <CardContent className="pt-6">
          {faculty.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No faculty found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Employee ID</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Department</th>
                    <th className="text-left py-3 px-4 font-medium">Designation</th>
                    <th className="text-left py-3 px-4 font-medium">Status</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {faculty.map((fac) => (
                    <tr key={fac.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 mono">{fac.employee_id}</td>
                      <td className="py-3 px-4">{fac.name}</td>
                      <td className="py-3 px-4">{getDepartmentName(fac.department_id)}</td>
                      <td className="py-3 px-4">{fac.designation}</td>
                      <td className="py-3 px-4">
                        {fac.is_class_incharge && (
                          <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                            Class Incharge
                          </Badge>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <Button variant="ghost" size="sm" onClick={() => setViewFaculty(fac)} data-testid={`view-faculty-${fac.id}`}>
                          <Eye className="h-4 w-4" />
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
    </div>
  );
}

// Students Page
function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDept, setSelectedDept] = useState('all');
  const [selectedYear, setSelectedYear] = useState('all');
  const [selectedQuota, setSelectedQuota] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
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
  }, [debouncedSearch, selectedDept, selectedYear, selectedQuota]);

  const loadData = async () => {
    try {
      setLoading(true);
      const params = {
        search: debouncedSearch || undefined,
        department_id: selectedDept !== 'all' ? selectedDept : undefined,
        year: selectedYear !== 'all' ? parseInt(selectedYear) : undefined,
        category: selectedQuota !== 'all' ? selectedQuota : undefined,
        limit: 100
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

  const getDepartmentName = (deptId) => {
    const dept = departments.find(d => d.id === deptId);
    return dept ? dept.name : 'Unknown';
  };

  if (loading && !students.length) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-4 py-4">
        <div className="relative flex-1 min-w-[240px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search students..."
            className="pl-9"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Select value={selectedDept} onValueChange={setSelectedDept}>
          <SelectTrigger className="w-48" data-testid="filter-dept-select">
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
          <SelectTrigger className="w-40">
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
      </div>

      <Card>
        <CardContent className="pt-6">
          {students.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No students found</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Reg No</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Department</th>
                    <th className="text-left py-3 px-4 font-medium">Batch</th>
                    <th className="text-left py-3 px-4 font-medium">Semester</th>
                    <th className="text-left py-3 px-4 font-medium">CGPA</th>
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
                      <td className="py-3 px-4 mono">{student.roll_number}</td>
                      <td className="py-3 px-4">
                        <div className="font-medium">{student.name}</div>
                        <div className="text-[10px] text-primary font-medium">{normalizeQuota(student.admission_quota)}</div>
                      </td>
                      <td className="py-3 px-4">{getDepartmentName(student.department_id)}</td>
                      <td className="py-3 px-4">{student.batch}</td>
                      <td className="py-3 px-4">{student.semester}</td>
                      <td className="py-3 px-4 mono font-medium">{student.cgpa?.toFixed(2) || '0.00'}</td>
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

// Risk Alerts Page
function RisksPage() {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRisks();
  }, []);

  const loadRisks = async () => {
    try {
      const response = await analyticsAPI.getDepartmentRisks();
      setRisks(response.data);
    } catch (error) {
      toast.error('Failed to load risk data');
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
      <h2 className="text-2xl font-bold">Risk Alerts</h2>

      <Card>
        <CardHeader>
          <CardTitle>At-Risk Students</CardTitle>
          <CardDescription>Students flagged by the AI risk scoring system</CardDescription>
        </CardHeader>
        <CardContent>
          {risks.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No at-risk students detected</p>
          ) : (
            <div className="space-y-4">
              {risks.map((risk, idx) => (
                <div key={idx} className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <p className="font-medium">{risk.name}</p>
                    <p className="text-sm text-muted-foreground mono">{risk.roll_number}</p>
                    <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                      <span>Attendance: {risk.attendance_percentage?.toFixed(1)}%</span>
                      <span>CGPA: {risk.cgpa?.toFixed(2) || 'N/A'}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className={getRiskColor(risk.risk_level)}>
                      {risk.risk_level}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      Score: {risk.risk_score?.toFixed(0)}
                    </p>
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

// Approvals Page
function ApprovalsPage() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      // Principal only sees requests explicitly forwarded by Admin (office)
      const response = await documentAPI.getAll();
      setRequests(response.data.filter(r => r.status === 'Verified' && r.current_level === 'principal'));
    } catch (error) {
      toast.error('Failed to load pending approvals');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (requestId) => {
    try {
      await documentAPI.approve(requestId);
      toast.success('Document request approved');
      loadRequests();
    } catch (error) {
      toast.error('Failed to approve document');
    }
  };

  const handleReject = async (requestId) => {
    const remarks = prompt("Enter rejection reason:");
    if (!remarks) return;
    try {
      await documentAPI.reject(requestId, remarks);
      toast.success('Document request rejected');
      loadRequests();
    } catch (error) {
      toast.error('Failed to reject document');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Document Approvals</h2>

      <Card>
        <CardHeader>
          <CardTitle>Requests Requiring Principal Approval</CardTitle>
          <CardDescription>Documents forwarded by the Administrative Office for institutional approval.</CardDescription>
        </CardHeader>
        <CardContent>
          {requests.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No documents awaiting approval</p>
          ) : (
            <div className="space-y-4">
              {requests.map((req) => (
                <div key={req.id} className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <p className="font-medium">{req.student_name}</p>
                    <p className="text-sm text-muted-foreground mono">{req.roll_number}</p>
                    <p className="text-sm font-semibold capitalize mt-1 text-primary">
                      {req.document_type.replace('_', ' ')}
                    </p>
                    {req.purpose && <p className="text-xs text-muted-foreground mt-1 italic">Purpose: {req.purpose}</p>}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleApprove(req.id)} className="text-emerald-600 border-emerald-600 hover:bg-emerald-50">
                      <FileCheck className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleReject(req.id)} className="text-red-600 border-red-600 hover:bg-red-50">
                      Reject
                    </Button>
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

// Fee Analytics Page
function FeesPage() {
  return <FeesAnalytics />;
}

// Audit Logs Page
function AuditLogsPage() {
  return <AuditLogs />;
}

// Grievance Management Page
function GrievanceManagementPage() {
  const [grievances, setGrievances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGrievance, setSelectedGrievance] = useState(null);
  const [resolution, setResolution] = useState('');

  useEffect(() => {
    loadGrievances();
  }, []);

  const loadGrievances = async () => {
    try {
      const response = await grievanceAPI.getAll({ current_level: 'principal' });
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
      <h2 className="text-2xl font-bold">Escalated Administrative Grievances</h2>

      <Dialog open={!!selectedGrievance} onOpenChange={() => { setSelectedGrievance(null); setResolution(''); }}>
        <DialogContent className="max-w-md" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Resolve Grievance</DialogTitle>
          </DialogHeader>
          {selectedGrievance && (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Subject</p>
                <p className="font-medium">{selectedGrievance.subject}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="text-sm">{selectedGrievance.description}</p>
              </div>
              <div className="space-y-2">
                <Label>Resolution</Label>
                <Textarea
                  data-testid="grievance-resolution-input"
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  placeholder="Enter resolution details..."
                  rows={4}
                />
              </div>
              <Button onClick={handleResolve} className="w-full" data-testid="submit-resolution-btn">
                Mark as Resolved
              </Button>
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
                      {grievance.status === 'open' && (
                        <Button size="sm" onClick={() => setSelectedGrievance(grievance)} data-testid={`resolve-grievance-${grievance.id}`}>
                          Resolve
                        </Button>
                      )}
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

// Announcements Page with CRUD
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
        const response = await facultyAPI.getMyProfile(); // Principal is also a user
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

import { DepartmentDetails } from '../../components/ui/DepartmentDetails';

// Main Dashboard Component
export default function PrincipalDashboard() {
  const { user } = useAuth();
  return (
    <DashboardLayout sidebarItems={sidebarItems} title="Principal Dashboard">
      <Routes>
        <Route index element={<DashboardOverview />} />
        <Route path="departments" element={<DepartmentsPage />} />
        <Route path="faculty" element={<FacultyPage />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="risks" element={<RisksPage />} />
        <Route path="grievances" element={<GrievanceManagementPage />} />
        <Route path="approvals" element={<ApprovalsPage />} />
        <Route path="fees" element={<FeesAnalytics />} />
        <Route path="audit" element={<AuditLogs />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="communications" element={<Communications userRole="principal" userId={user?.id} />} />
        <Route path="settings" element={<SettingsPageWrapper />} />
        <Route path="profile" element={<ProfilePageWrapper />} />
        <Route path="department/:id" element={<DepartmentDetails />} />
      </Routes>
    </DashboardLayout>
  );
}
