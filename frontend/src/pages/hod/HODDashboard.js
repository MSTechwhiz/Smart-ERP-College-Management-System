import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpen,
  AlertTriangle,
  BarChart3,
  Settings,
  UserCog,
  FileCheck,
  Plus,
  Eye,
  Megaphone,
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
import {
  studentAPI,
  facultyAPI,
  subjectAPI,
  analyticsAPI,
  documentAPI,
  marksAPI,
  leaveAPI,
  grievanceAPI,
  announcementAPI
} from '../../services/api';
import { toast } from 'sonner';
import { useAuth } from '../../context/AuthContext';
import { getRiskColor, formatDateTime, getYearLabel } from '../../lib/utils';
import { Communications } from '../shared/Communications';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const sidebarItems = [
  { icon: LayoutDashboard, label: 'Dashboard', href: '/hod' },
  { icon: GraduationCap, label: 'Students', href: '/hod/students' },
  { icon: Users, label: 'Faculty', href: '/hod/faculty' },
  { icon: BookOpen, label: 'Subjects', href: '/hod/subjects' },
  { icon: UserCog, label: 'Subject Mapping', href: '/hod/mapping' },
  { icon: AlertTriangle, label: 'Risk Alerts', href: '/hod/risks' },
  { icon: FileCheck, label: 'Approvals', href: '/hod/approvals' },
  { icon: MessageSquare, label: 'Grievances', href: '/hod/grievances' },
  { icon: Megaphone, label: 'Announcements', href: '/hod/announcements' },
  { icon: MessageSquare, label: 'Communications', href: '/hod/communications' },
  { icon: BarChart3, label: 'Analytics', href: '/hod/analytics' },
  { icon: Settings, label: 'Settings', href: '/hod/settings' },
];

// Dashboard Overview
function DashboardOverview() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({ students: 0, faculty: 0, subjects: 0, pendingApprovals: 0 });
  const [risks, setRisks] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    try {
      const [studentsRes, facultyRes, subjectsRes, risksRes, leaveRes, annRes] = await Promise.all([
        studentAPI.getAll({ department_id: user?.department_id }),
        facultyAPI.getAll({ department_id: user?.department_id }),
        subjectAPI.getAll({ department_id: user?.department_id }),
        analyticsAPI.getDepartmentRisks().catch(() => ({ data: [] })),
        leaveAPI.getAll({ status: 'pending' }).catch(() => ({ data: [] })),
        announcementAPI.getAll().catch(() => ({ data: [] }))
      ]);
      setStats({
        students: studentsRes.data.students?.length || 0,
        faculty: facultyRes.data.length,
        subjects: subjectsRes.data.length,
        pendingApprovals: leaveRes.data.length
      });
      setRisks(risksRes.data.slice(0, 5));
      setAnnouncements(annRes.data.slice(0, 3));
    } catch (error) {
      console.error('Error loading dashboard:', error);
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
      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/hod/students')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Department Students</p>
                <p className="text-3xl font-bold mono">{stats.students}</p>
              </div>
              <GraduationCap className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/hod/faculty')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Faculty Members</p>
                <p className="text-3xl font-bold mono">{stats.faculty}</p>
              </div>
              <Users className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/hod/subjects')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Subjects</p>
                <p className="text-3xl font-bold mono">{stats.subjects}</p>
              </div>
              <BookOpen className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="stat-card cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/hod/approvals')}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Approvals</p>
                <p className="text-3xl font-bold mono">{stats.pendingApprovals}</p>
              </div>
              <FileCheck className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="assign-faculty-btn" onClick={() => navigate('/hod/mapping')}>
              <UserCog className="h-5 w-5" />
              <span>Assign Faculty</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="approve-marks-btn" onClick={() => navigate('/hod/approvals')}>
              <FileCheck className="h-5 w-5" />
              <span>Approve Docs</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="view-analytics-btn" onClick={() => navigate('/hod/analytics')}>
              <BarChart3 className="h-5 w-5" />
              <span>Analytics</span>
            </Button>
            <Button variant="outline" className="h-auto py-4 flex-col gap-2" data-testid="view-risks-btn" onClick={() => navigate('/hod/risks')}>
              <AlertTriangle className="h-5 w-5" />
              <span>Risk Alerts</span>
            </Button>
          </CardContent>
        </Card>

        {/* Risk Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-600" />
              At-Risk Students
            </CardTitle>
          </CardHeader>
          <CardContent>
            {risks.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">No at-risk students detected</p>
            ) : (
              <div className="space-y-3">
                {risks.map((risk, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div>
                      <p className="font-medium">{risk.name}</p>
                      <p className="text-sm text-muted-foreground mono">{risk.roll_number}</p>
                    </div>
                    <div className="text-right">
                      <Badge className={getRiskColor(risk.risk_level)}>
                        {risk.risk_level}
                      </Badge>
                      <p className="text-xs text-muted-foreground mt-1">
                        {risk.attendance_percentage?.toFixed(1)}% attendance
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
                  onClick={() => navigate('/hod/announcements')}
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
                onClick={() => navigate('/hod/announcements')}
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

// Students Page
function StudentsPage() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewStudent, setViewStudent] = useState(null);
  const [selectedYear, setSelectedYear] = useState('All');

  const yearFilters = ['All', '1st Year', '2nd Year', '3rd Year', 'Final Year'];

  useEffect(() => {
    loadStudents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadStudents = async () => {
    try {
      const response = await studentAPI.getAll({ department_id: user?.department_id });
      setStudents(response.data.students || []);
    } catch (error) {
      toast.error('Failed to load students');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  const filteredStudents = selectedYear === 'All'
    ? students
    : students.filter(s => getYearLabel(s.semester) === selectedYear);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h2 className="text-2xl font-bold">Department Students</h2>
        <div className="flex flex-wrap gap-2 p-1 bg-muted rounded-lg w-fit">
          {yearFilters.map((year) => (
            <Button
              key={year}
              variant={selectedYear === year ? "default" : "ghost"}
              size="sm"
              onClick={() => setSelectedYear(year)}
              className="px-3 h-8 text-xs font-medium"
            >
              {year === 'All' ? 'All' : year.replace(' Year', ' Yr')}
            </Button>
          ))}
        </div>
      </div>

      {/* View Student Dialog */}
      <Dialog open={!!viewStudent} onOpenChange={() => setViewStudent(null)}>
        <DialogContent className="max-w-md" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Student Details</DialogTitle>
          </DialogHeader>
          {viewStudent && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-medium">{viewStudent.name}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Email</p>
                <p className="font-medium">{viewStudent.email}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Student ID (System Generated)</p>
                <p className="font-medium mono">{viewStudent.roll_number}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Roll Number</p>
                <p className="font-medium mono">{viewStudent.register_number || '-'}</p>
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
                <p className="text-sm text-muted-foreground">CGPA</p>
                <p className="font-medium mono">
                  {(!viewStudent.cgpa || viewStudent.cgpa === 0) ? 'N/A' : viewStudent.cgpa.toFixed(2)}
                </p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Card>
        <CardContent className="pt-6">
          {filteredStudents.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              {students.length === 0 ? "No students in department" : `No students found for ${selectedYear}`}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Reg No</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Batch</th>
                    <th className="text-left py-3 px-4 font-medium">Semester</th>
                    <th className="text-left py-3 px-4 font-medium">Section</th>
                    <th className="text-left py-3 px-4 font-medium">CGPA</th>
                    <th className="text-left py-3 px-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredStudents.map((student) => (
                    <tr key={student.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 mono">{student.roll_number}</td>
                      <td className="py-3 px-4">{student.name}</td>
                      <td className="py-3 px-4">{student.batch}</td>
                      <td className="py-3 px-4">{getYearLabel(student.semester)}</td>
                      <td className="py-3 px-4">{student.semester}</td>
                      <td className="py-3 px-4">{student.section || '-'}</td>
                      <td className="py-3 px-4 mono font-medium">{student.cgpa?.toFixed(2) || '0.00'}</td>
                      <td className="py-3 px-4">
                        <Button variant="ghost" size="sm" onClick={() => setViewStudent(student)} data-testid={`view-student-${student.id}`}>
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

// Faculty Page with Class Incharge Assignment
function FacultyPage() {
  const { user } = useAuth();
  const [faculty, setFaculty] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFaculty, setSelectedFaculty] = useState(null);
  const [inchargeClass, setInchargeClass] = useState('');

  useEffect(() => {
    loadFaculty();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadFaculty = async () => {
    try {
      const response = await facultyAPI.getAll({ department_id: user?.department_id });
      setFaculty(response.data);
    } catch (error) {
      toast.error('Failed to load faculty');
    } finally {
      setLoading(false);
    }
  };

  const handleAssignIncharge = async () => {
    if (!inchargeClass.trim()) {
      toast.error('Please enter class details');
      return;
    }
    try {
      await facultyAPI.assignClassIncharge(selectedFaculty.id, inchargeClass);
      toast.success('Class incharge assigned successfully');
      setSelectedFaculty(null);
      setInchargeClass('');
      loadFaculty();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to assign class incharge');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Department Faculty</h2>

      {/* Assign Incharge Dialog */}
      <Dialog open={!!selectedFaculty} onOpenChange={() => { setSelectedFaculty(null); setInchargeClass(''); }}>
        <DialogContent className="max-w-sm" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Assign Class Incharge</DialogTitle>
            <DialogDescription>
              Assign {selectedFaculty?.name} as class incharge
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Class (Section-Semester)</Label>
              <Input
                data-testid="incharge-class-input"
                value={inchargeClass}
                onChange={(e) => setInchargeClass(e.target.value)}
                placeholder="e.g., CSE-A-5"
              />
            </div>
            <Button onClick={handleAssignIncharge} className="w-full" data-testid="submit-incharge-btn">
              Assign
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {faculty.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="py-8 text-center text-muted-foreground">
              No faculty members in department
            </CardContent>
          </Card>
        ) : (
          faculty.map((fac) => (
            <Card key={fac.id} className="card-interactive">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="h-12 w-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                    <Users className="h-6 w-6 text-emerald-600" />
                  </div>
                  {fac.is_class_incharge && (
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
                      Class Incharge
                    </Badge>
                  )}
                </div>
                <h3 className="font-semibold">{fac.name}</h3>
                <p className="text-sm text-muted-foreground mb-2">{fac.designation}</p>
                <p className="text-xs mono text-muted-foreground">{fac.employee_id}</p>
                {fac.incharge_class && (
                  <p className="text-xs mt-2">Incharge: {fac.incharge_class}</p>
                )}
                <div className="mt-4 flex justify-end">
                  <Button variant="outline" size="sm" onClick={() => setSelectedFaculty(fac)} data-testid={`assign-incharge-${fac.id}`}>
                    <UserCog className="h-4 w-4 mr-1" />
                    Assign Incharge
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

// Subjects Page with CRUD
function SubjectsPage() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    code: '', name: '', semester: 1, credits: 3, subject_type: 'theory', regulation: 'R2023'
  });

  useEffect(() => {
    loadSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadSubjects = async () => {
    try {
      const response = await subjectAPI.getAll({ department_id: user?.department_id });
      setSubjects(response.data);
    } catch (error) {
      toast.error('Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await subjectAPI.create({
        ...formData,
        department_id: user?.department_id || '',
        semester: parseInt(formData.semester),
        credits: parseInt(formData.credits)
      });
      toast.success('Subject created successfully');
      setDialogOpen(false);
      setFormData({ code: '', name: '', semester: 1, credits: 3, subject_type: 'theory', regulation: 'R2023' });
      loadSubjects();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create subject');
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
        <h2 className="text-2xl font-bold">Subject Management</h2>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-subject-btn">
              <Plus className="h-4 w-4 mr-2" />
              Add Subject
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md" aria-describedby={undefined}>
            <DialogHeader>
              <DialogTitle>Add New Subject</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Subject Code</Label>
                  <Input
                    data-testid="subject-code-input"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                    placeholder="CS301"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Subject Name</Label>
                  <Input
                    data-testid="subject-name-input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Data Structures"
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Semester</Label>
                  <Input
                    type="number"
                    min="1"
                    max="8"
                    data-testid="subject-semester-input"
                    value={formData.semester}
                    onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Credits</Label>
                  <Input
                    type="number"
                    min="1"
                    max="6"
                    data-testid="subject-credits-input"
                    value={formData.credits}
                    onChange={(e) => setFormData({ ...formData, credits: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select value={formData.subject_type} onValueChange={(v) => setFormData({ ...formData, subject_type: v })}>
                    <SelectTrigger data-testid="subject-type-select">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="theory">Theory</SelectItem>
                      <SelectItem value="lab">Lab</SelectItem>
                      <SelectItem value="project">Project</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="space-y-2">
                <Label>Regulation</Label>
                <Input
                  value={formData.regulation}
                  onChange={(e) => setFormData({ ...formData, regulation: e.target.value.toUpperCase() })}
                  placeholder="e.g., R2023"
                  required
                />
              </div>
              <Button type="submit" className="w-full" data-testid="submit-subject-btn">Create Subject</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="pt-6">
          {subjects.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No subjects found. Click "Add Subject" to create one.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Code</th>
                    <th className="text-left py-3 px-4 font-medium">Name</th>
                    <th className="text-left py-3 px-4 font-medium">Semester</th>
                    <th className="text-left py-3 px-4 font-medium">Credits</th>
                    <th className="text-left py-3 px-4 font-medium">Type</th>
                  </tr>
                </thead>
                <tbody>
                  {subjects.map((subject) => (
                    <tr key={subject.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 mono font-medium">{subject.code}</td>
                      <td className="py-3 px-4">{subject.name}</td>
                      <td className="py-3 px-4">{getYearLabel(subject.semester)} ({subject.semester})</td>
                      <td className="py-3 px-4">{subject.credits}</td>
                      <td className="py-3 px-4 capitalize">{subject.subject_type}</td>
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

// Subject-Faculty Mapping Page
function SubjectMappingPage() {
  const { user } = useAuth();
  const [subjects, setSubjects] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [mappings, setMappings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [filterYear, setFilterYear] = useState('2024-25');
  const [filterSemester, setFilterSemester] = useState('5');
  const [formData, setFormData] = useState({
    subject_id: '',
    faculty_id: '',
    section: '',
    academic_year: filterYear,
    semester: filterSemester,
    day: 'Monday',
    period: '1',
    start_time: '09:00',
    end_time: '09:50'
  });

  // Calculate year selection based on semester
  const getYearFromSemester = (sem) => {
    const s = parseInt(sem);
    if (s <= 2) return "1";
    if (s <= 4) return "2";
    if (s <= 6) return "3";
    return "4";
  };

  const [selectedYear, setSelectedYear] = useState(getYearFromSemester(filterSemester));

  const getSemestersForYear = (year) => {
    switch (year) {
      case "1": return [1, 2];
      case "2": return [3, 4];
      case "3": return [5, 6];
      case "4": return [7, 8];
      default: return [1, 2];
    }
  };

  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      academic_year: filterYear,
      semester: filterSemester
    }));
    setSelectedYear(getYearFromSemester(filterSemester));
  }, [filterYear, filterSemester, dialogOpen]);

  const selectedYearLabel = getYearLabel(filterSemester);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterYear, filterSemester, user?.department_id]);

  const loadData = async () => {
    try {
      if (!user?.department_id) {
        console.warn('Waiting for department_id to load...');
        return;
      }
      const queryParams = { 
        academic_year: filterYear || '2024-25', 
        semester: parseInt(filterSemester) || 1,
        department_id: user.department_id 
      };
      const [subjectsRes, facultyRes, mappingsRes] = await Promise.all([
        subjectAPI.getAll({ department_id: user?.department_id }),
        facultyAPI.getAll({ department_id: user?.department_id }),
        subjectAPI.getMappings(queryParams)
      ]);
      setSubjects(subjectsRes.data);
      setFaculty(facultyRes.data);
      setMappings(mappingsRes.data);
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await subjectAPI.createMapping({
        ...formData,
        semester: parseInt(formData.semester),
        period: parseInt(formData.period)
      });
      toast.success('Subject mapped to faculty successfully');
      setDialogOpen(false);
      setFormData({ 
        subject_id: '', faculty_id: '', section: 'A', academic_year: filterYear, semester: parseInt(filterSemester),
        day: 'Monday', period: 1, start_time: '09:00', end_time: '10:00'
      });
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create mapping');
    }
  };

  const getFacultyName = (facultyId) => {
    const fac = faculty.find(f => f.id === facultyId);
    return fac ? fac.name : 'Unknown';
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Subject-Faculty Mapping</h2>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Label className="whitespace-nowrap">Year</Label>
            <Select 
              value={getYearFromSemester(filterSemester)} 
              onValueChange={(v) => {
                const firstSem = getSemestersForYear(v)[0].toString();
                setFilterSemester(firstSem);
              }}
            >
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">1st Year</SelectItem>
                <SelectItem value="2">2nd Year</SelectItem>
                <SelectItem value="3">3rd Year</SelectItem>
                <SelectItem value="4">Final Year</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <Label className="whitespace-nowrap">Semester</Label>
            <Select value={filterSemester} onValueChange={setFilterSemester}>
              <SelectTrigger className="w-[80px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {[1, 2, 3, 4, 5, 6, 7, 8].map(s => (
                  <SelectItem key={s} value={s.toString()}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button data-testid="add-mapping-btn">
              <Plus className="h-4 w-4 mr-2" />
              Add Mapping
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md" aria-describedby={undefined}>
            <DialogHeader>
              <DialogTitle>Map Subject to Faculty</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <Label>Subject</Label>
                <Select value={formData.subject_id} onValueChange={(v) => setFormData({ ...formData, subject_id: v })}>
                  <SelectTrigger data-testid="mapping-subject-select">
                    <SelectValue placeholder="Select subject" />
                  </SelectTrigger>
                  <SelectContent>
                    {subjects.map((subj) => (
                      <SelectItem key={subj.id} value={subj.id}>
                        {subj.code} - {subj.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Faculty</Label>
                <Select value={formData.faculty_id} onValueChange={(v) => setFormData({ ...formData, faculty_id: v })}>
                  <SelectTrigger data-testid="mapping-faculty-select">
                    <SelectValue placeholder="Select faculty" />
                  </SelectTrigger>
                  <SelectContent>
                    {faculty.map((fac) => (
                      <SelectItem key={fac.id} value={fac.id}>
                        {fac.name} ({fac.employee_id})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Section</Label>
                  <Input
                    data-testid="mapping-section-input"
                    value={formData.section}
                    onChange={(e) => setFormData({ ...formData, section: e.target.value.toUpperCase() })}
                    placeholder="A"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Year</Label>
                  <Select 
                    value={selectedYear} 
                    onValueChange={(v) => {
                      setSelectedYear(v);
                      setFormData({ ...formData, semester: getSemestersForYear(v)[0].toString() });
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1st Year</SelectItem>
                      <SelectItem value="2">2nd Year</SelectItem>
                      <SelectItem value="3">3rd Year</SelectItem>
                      <SelectItem value="4">Final Year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Semester</Label>
                  <Select 
                    value={formData.semester.toString()} 
                    onValueChange={(v) => setFormData({ ...formData, semester: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {getSemestersForYear(selectedYear).map(s => (
                        <SelectItem key={s} value={s.toString()}>{s}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Day</Label>
                  <Select value={formData.day} onValueChange={(v) => setFormData({ ...formData, day: v })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'].map(day => (
                        <SelectItem key={day} value={day}>{day}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Period (1-7)</Label>
                  <Input
                    type="number"
                    min="1"
                    max="7"
                    value={formData.period}
                    onChange={(e) => setFormData({ ...formData, period: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Start Time</Label>
                  <Input
                    type="time"
                    value={formData.start_time}
                    onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>End Time</Label>
                  <Input
                    type="time"
                    value={formData.end_time}
                    onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full" data-testid="submit-mapping-btn">Create Mapping</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="pt-6">
          {mappings.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">No mappings found. Click "Add Mapping" to assign faculty to subjects.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium">Subject</th>
                    <th className="text-left py-3 px-4 font-medium">Faculty</th>
                    <th className="text-left py-3 px-4 font-medium">Schedule</th>
                     <th className="text-left py-3 px-4 font-medium">Section</th>
                     <th className="text-left py-3 px-4 font-medium">Year / Semester</th>
                  </tr>
                </thead>
                <tbody>
                  {mappings.map((mapping) => (
                    <tr key={mapping.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 font-medium">
                        <p className="font-semibold">{mapping.subject_name}</p>
                        <p className="text-xs text-muted-foreground mono">{mapping.subject_code}</p>
                      </td>
                      <td className="py-3 px-4">{getFacultyName(mapping.faculty_id)}</td>
                      <td className="py-3 px-4">
                        <Badge variant="outline">
                          {mapping.day} | Per {mapping.period}
                        </Badge>
                        <p className="text-[10px] text-muted-foreground mt-1">
                          {mapping.start_time} - {mapping.end_time}
                        </p>
                      </td>
                       <td className="py-3 px-4 mono">{mapping.section}</td>
                       <td className="py-3 px-4 whitespace-nowrap">
                         <div className="font-medium text-sm">{getYearLabel(mapping.semester)}</div>
                         <div className="text-[10px] text-muted-foreground">Sem {mapping.semester} • {mapping.academic_year}</div>
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

// Approvals Page with Enhanced Grievance Workflow
function ApprovalsPage() {
  const [leaveRequests, setLeaveRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await leaveAPI.getHODPending();
      setLeaveRequests(response.data);
    } catch (error) {
      console.error("Error loading approvals:", error);
      toast.error('Failed to load approvals data');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveLeave = async (requestId, approved) => {
    try {
      await leaveAPI.approve(requestId, approved);
      toast.success(`Leave request ${approved ? 'approved' : 'rejected'}`);
      loadData();
    } catch (error) {
      toast.error('Failed to process leave request');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Pending Approvals</h2>

      {/* Leave Requests SECTION 1 */}
      <Card>
        <CardHeader>
          <CardTitle>Leave Requests</CardTitle>
          <CardDescription>Student leave applications requiring HOD approval</CardDescription>
        </CardHeader>
        <CardContent>
          {leaveRequests.length === 0 ? (
            <p className="text-center text-muted-foreground py-4">No pending leave requests</p>
          ) : (
            <div className="space-y-4">
              {leaveRequests.map((req) => (
                <div key={req.id} className="flex items-center justify-between p-4 rounded-lg border">
                  <div>
                    <p className="font-medium">{req.student_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {req.department_name} • {req.from_date} to {req.to_date}
                    </p>
                    <p className="text-xs mt-1 italic">Reason: {req.reason}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleApproveLeave(req.id, false)} className="text-red-600 border-red-600 hover:bg-red-50">
                      Reject
                    </Button>
                    <Button size="sm" onClick={() => handleApproveLeave(req.id, true)} className="bg-emerald-600 hover:bg-emerald-700">
                      Approve
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

// Grievances Page
function GrievancesPage() {
  const [grievances, setGrievances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGrievance, setSelectedGrievance] = useState(null);
  const [resolution, setResolution] = useState('');
  const [actionType, setActionType] = useState('resolve'); // 'resolve', 'comment'
  const [remarks, setRemarks] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await grievanceAPI.getHODPendingGrievances();
      setGrievances(response.data);
    } catch (error) {
      console.error("Error loading grievances:", error);
      toast.error('Failed to load grievances');
    } finally {
      setLoading(false);
    }
  };

  const handleResolveGrievance = async () => {
    if (!resolution.trim()) {
      toast.error('Please enter a resolution');
      return;
    }
    try {
      await grievanceAPI.resolve(selectedGrievance.id, resolution);
      toast.success('Grievance resolved successfully');
      setSelectedGrievance(null);
      setResolution('');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to resolve grievance');
    }
  };

  const handleAddComment = async () => {
    if (!remarks.trim()) {
      toast.error('Please enter a comment');
      return;
    }
    try {
      await grievanceAPI.addComment(selectedGrievance.id, remarks);
      toast.success('Comment added');
      setRemarks('');
      loadData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add comment');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Faculty Escalated Grievances</h2>

      {/* Grievance Action Dialog */}
      <Dialog open={!!selectedGrievance} onOpenChange={() => { setSelectedGrievance(null); setResolution(''); setRemarks(''); setActionType('resolve'); }}>
        <DialogContent className="max-w-lg" aria-describedby={undefined}>
          <DialogHeader>
            <DialogTitle>Handle Grievance</DialogTitle>
            <CardDescription>Ticket: {selectedGrievance?.ticket_id || selectedGrievance?.id?.slice(-8)}</CardDescription>
          </DialogHeader>
          {selectedGrievance && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 p-3 bg-muted/50 rounded-lg">
                <div>
                  <p className="text-xs text-muted-foreground">Student</p>
                  <p className="font-medium text-sm">{selectedGrievance.student_name} ({selectedGrievance.roll_number})</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Category</p>
                  <p className="font-medium text-sm capitalize">{selectedGrievance.category}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Subject</p>
                <p className="font-medium">{selectedGrievance.subject}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Description</p>
                <p className="text-sm p-2 bg-muted/30 rounded">{selectedGrievance.description}</p>
              </div>
              {selectedGrievance.faculty_remarks_for_hod && (
                <div>
                  <p className="text-sm text-amber-600 font-medium">Faculty Remarks</p>
                  <p className="text-sm p-2 bg-amber-50 dark:bg-amber-950/20 rounded border border-amber-100 dark:border-amber-900/30 italic">
                    {selectedGrievance.faculty_remarks_for_hod}
                  </p>
                </div>
              )}

              <div className="flex rounded-lg bg-muted p-1">
                <Button variant={actionType === 'resolve' ? 'default' : 'ghost'} size="sm" className="flex-1" onClick={() => setActionType('resolve')}>Resolve</Button>
                <Button variant={actionType === 'comment' ? 'default' : 'ghost'} size="sm" className="flex-1" onClick={() => setActionType('comment')}>Comment</Button>
              </div>

              {actionType === 'resolve' && (
                <div className="space-y-2">
                  <Label>Resolution</Label>
                  <Textarea value={resolution} onChange={(e) => setResolution(e.target.value)} placeholder="Enter resolution details..." rows={3} />
                  <Button onClick={handleResolveGrievance} className="w-full">Mark as Resolved</Button>
                </div>
              )}
              {actionType === 'comment' && (
                <div className="space-y-2">
                  <Label>Response to Student</Label>
                  <Textarea value={remarks} onChange={(e) => setRemarks(e.target.value)} placeholder="Add your response..." rows={2} />
                  <Button onClick={handleAddComment} className="w-full">Send Response</Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      <div className="grid grid-cols-1 gap-4">
        {grievances.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <MessageSquare className="h-12 w-12 text-muted-foreground/20 mb-4" />
              <p className="text-muted-foreground font-medium">No escalated grievances to review</p>
            </CardContent>
          </Card>
        ) : (
          grievances.map((grievance) => (
            <Card key={grievance.id} className="hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-semibold">{grievance.subject}</h4>
                    <p className="text-sm text-muted-foreground">
                      From: <span className="font-medium text-foreground">{grievance.student_name}</span> • {grievance.roll_number}
                    </p>
                  </div>
                  <Badge variant="secondary" className="bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200">
                    Faculty Escalated
                  </Badge>
                </div>

                <p className="text-sm text-muted-foreground mb-4 line-clamp-2 italic">
                  "{grievance.description}"
                </p>

                {grievance.faculty_remarks_for_hod && (
                  <div className="mb-4 p-3 bg-muted/30 rounded-lg border border-dashed text-sm">
                    <p className="font-medium text-xs uppercase tracking-wider text-muted-foreground mb-1">Faculty Remarks</p>
                    <p className="text-foreground">{grievance.faculty_remarks_for_hod}</p>
                  </div>
                )}

                <div className="flex items-center justify-between mt-6 pt-4 border-t">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Escalated on: {formatDateTime(grievance.updated_at || grievance.created_at)}</span>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => {
                      setSelectedGrievance(grievance);
                      setActionType('comment');
                    }}>
                      Respond
                    </Button>
                    <Button size="sm" onClick={() => {
                      setSelectedGrievance(grievance);
                      setActionType('resolve');
                    }}>
                      Resolve
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Risk Alerts Page
function RisksPage() {
  const { user } = useAuth();
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRisks();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadRisks = async () => {
    try {
      const response = await analyticsAPI.getDepartmentRisks({ department_id: user?.department_id });
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
        <CardContent className="pt-6">
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

// Analytics Page
function AnalyticsPage() {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadData = async () => {
    try {
      const response = await studentAPI.getAll({ department_id: user?.department_id });
      setStudents(response.data.students || []);
    } catch (error) {
      console.error('Error loading analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>;
  }

  // Calculate CGPA distribution
  const cgpaDistribution = students.reduce((acc, s) => {
    const cgpa = s.cgpa || 0;
    if (cgpa >= 9) acc['9-10']++;
    else if (cgpa >= 8) acc['8-9']++;
    else if (cgpa >= 7) acc['7-8']++;
    else if (cgpa >= 6) acc['6-7']++;
    else acc['<6']++;
    return acc;
  }, { '9-10': 0, '8-9': 0, '7-8': 0, '6-7': 0, '<6': 0 });

  const chartData = Object.entries(cgpaDistribution).map(([range, count]) => ({
    name: range,
    count
  }));

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Department Analytics</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>CGPA Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
                <span>Total Students</span>
                <span className="font-bold mono">{students.length}</span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
                <span>Average CGPA</span>
                <span className="font-bold mono">
                  {students.length > 0
                    ? (students.reduce((sum, s) => sum + (s.cgpa || 0), 0) / students.length).toFixed(2)
                    : '0.00'}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
                <span>Top Performers (CGPA 9+)</span>
                <span className="font-bold mono">{cgpaDistribution['9-10']}</span>
              </div>
              <div className="flex justify-between items-center p-3 rounded-lg bg-muted/50">
                <span>At Risk (CGPA &lt;6)</span>
                <span className="font-bold mono text-red-600">{cgpaDistribution['<6']}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

import AnnouncementsPage from '../common/AnnouncementsPage';

// Settings Page
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
        const response = await facultyAPI.getMyProfile(); // HOD is also a faculty/user
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

export default function HODDashboard() {
  const { user } = useAuth();
  return (
    <DashboardLayout sidebarItems={sidebarItems} title="HOD Dashboard">
      <Routes>
        <Route index element={<DashboardOverview />} />
        <Route path="students" element={<StudentsPage />} />
        <Route path="faculty" element={<FacultyPage />} />
        <Route path="subjects" element={<SubjectsPage />} />
        <Route path="mapping" element={<SubjectMappingPage />} />
        <Route path="risks" element={<RisksPage />} />
        <Route path="approvals" element={<ApprovalsPage />} />
        <Route path="grievances" element={<GrievancesPage />} />
        <Route path="announcements" element={<AnnouncementsPage />} />
        <Route path="communications" element={<Communications userRole="hod" userId={user?.id} />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="settings" element={<SharedSettingsPage />} /> {/* Changed to SharedSettingsPage directly */}
        <Route path="profile" element={<ProfilePageWrapper />} />
      </Routes>
    </DashboardLayout>
  );
}
