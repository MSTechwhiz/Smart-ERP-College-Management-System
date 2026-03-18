import React, { useState, useEffect } from 'react';
import {
  Plus,
  Pencil,
  Trash2,
  Megaphone,
  Users,
  Building2,
  Filter,
  Calendar
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
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
} from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import { Checkbox } from '../../components/ui/checkbox';
import { announcementAPI, departmentAPI } from '../../services/api';
import { toast } from 'sonner';
import { formatDateTime } from '../../lib/utils';
import { useAuth } from '../../context/AuthContext';

export default function AnnouncementsPage({ adminView = false }) {
  const { user } = useAuth();
  const [announcements, setAnnouncements] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingAnn, setEditingAnn] = useState(null);

  const audienceOptionsByRole = {
    admin: [
      { value: 'principal', label: 'Principal' },
      { value: 'hod', label: 'HOD' },
      { value: 'faculty', label: 'Faculty' },
      { value: 'student', label: 'Students' },
    ],
    principal: [
      { value: 'hod', label: 'HOD' },
      { value: 'faculty', label: 'Faculty' },
      { value: 'student', label: 'Students' },
    ],
    hod: [
      { value: 'faculty', label: 'Faculty' },
      { value: 'student', label: 'Students' },
    ],
    faculty: [
      { value: 'student', label: 'Students' },
    ],
  };
  const audienceOptions = audienceOptionsByRole[user?.role] || [];
  
  const initialFormData = {
    title: '',
    content: '',
    target_roles: [],
    target_departments: user?.role === 'hod' || user?.role === 'faculty' ? [user?.department_id] : [],
    publish_date: new Date().toISOString().split('T')[0]
  };
  
  const [formData, setFormData] = useState(initialFormData);

  useEffect(() => {
    loadAnnouncements();
    if (adminView || user?.role === 'admin' || user?.role === 'principal') {
      loadDepartments();
    }
  }, []);

  const loadAnnouncements = async () => {
    try {
      const response = adminView ? await announcementAPI.getAll() : await announcementAPI.getAll(); 
      // Actually announcementAPI.getAll() in api.js uses /announcements which filters based on user
      setAnnouncements(response.data);
    } catch (error) {
      console.error('Failed to load announcements');
    } finally {
      setLoading(false);
    }
  };

  const loadDepartments = async () => {
    try {
      const response = await departmentAPI.getAll();
      setDepartments(response.data);
    } catch (error) {
      console.error('Failed to load departments');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingAnn) {
        await announcementAPI.update(editingAnn.id, formData);
        toast.success('Announcement updated');
      } else {
        await announcementAPI.create(formData);
        toast.success('Announcement published');
      }
      setDialogOpen(false);
      setEditingAnn(null);
      setFormData(initialFormData);
      loadAnnouncements();
    } catch (error) {
      toast.error(error.response?.data?.message || 'Operation failed');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this announcement?')) return;
    try {
      await announcementAPI.delete(id);
      toast.success('Announcement deleted');
      loadAnnouncements();
    } catch (error) {
      toast.error('Failed to delete');
    }
  };

  const handleEdit = (ann) => {
    setEditingAnn(ann);
    setFormData({
      title: ann.title,
      content: ann.content,
      target_roles: ann.target_roles || [],
      target_departments: ann.target_departments || [],
      publish_date: ann.publish_date?.split('T')[0]
    });
    setDialogOpen(true);
  };

  const toggleRole = (role) => {
    const roles = [...formData.target_roles];
    if (roles.includes(role)) {
      setFormData({ ...formData, target_roles: roles.filter(r => r !== role) });
    } else {
      setFormData({ ...formData, target_roles: [...roles, role] });
    }
  };

  const canManage = adminView || user?.role === 'admin' || user?.role === 'principal' || user?.role === 'hod' || user?.role === 'faculty';

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Announcements</h2>
          <p className="text-sm text-muted-foreground">Stay updated with latest college news</p>
        </div>
        
        {canManage && (
          <Dialog open={dialogOpen} onOpenChange={(open) => {
            setDialogOpen(open);
            if (!open) {
              setEditingAnn(null);
              setFormData(initialFormData);
            }
          }}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Announcement
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>{editingAnn ? 'Edit Announcement' : 'Create Announcement'}</DialogTitle>
                <DialogDescription>
                  {editingAnn ? 'Update the details of your announcement.' : 'Fill in the details below to post a new announcement to the college.'}
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>Title</Label>
                  <Input 
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    placeholder="Enter title"
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label>Content</Label>
                  <Textarea 
                    value={formData.content}
                    onChange={(e) => setFormData({...formData, content: e.target.value})}
                    placeholder="Write announcement details..."
                    rows={4}
                    required
                  />
                </div>
                
                <div className="space-y-3">
                  <Label>Target Audience Roles</Label>
                  <div className="grid grid-cols-2 gap-2">
                    {audienceOptions.map(({ value, label }) => (
                      <div key={value} className="flex items-center space-x-2">
                        <Checkbox 
                          id={`role-${value}`}
                          checked={formData.target_roles.includes(value)}
                          onCheckedChange={() => toggleRole(value)}
                        />
                        <Label htmlFor={`role-${value}`} className="cursor-pointer">{label}</Label>
                      </div>
                    ))}
                  </div>
                  <p className="text-[10px] text-muted-foreground">Leave empty for all roles</p>
                </div>

                <div className="space-y-2">
                  <Label>Publish Date</Label>
                  <Input 
                    type="date"
                    value={formData.publish_date}
                    onChange={(e) => setFormData({...formData, publish_date: e.target.value})}
                  />
                </div>

                <Button type="submit" className="w-full mt-4">
                  {editingAnn ? 'Update' : 'Publish'} Announcement
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        )}
      </div>

      <div className="grid gap-4">
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : announcements.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center text-muted-foreground">
              <Megaphone className="h-12 w-12 mx-auto mb-4 opacity-20" />
              <p>No announcements found</p>
            </CardContent>
          </Card>
        ) : (
          announcements.map((ann) => (
            <Card key={ann.id} className="overflow-hidden border-l-4 border-l-primary">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="space-y-1">
                    <h3 className="text-lg font-bold leading-tight">{ann.title}</h3>
                    <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDateTime(ann.publish_date)}
                      </span>
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        Posted by: {ann.created_by_name || 'System'}
                      </span>
                    </div>
                  </div>
                  
                  {canManage && (ann.created_by === user?.id || user?.role === 'admin') && (
                    <div className="flex gap-1">
                      <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => handleEdit(ann)}>
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => handleDelete(ann.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
                
                <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed mb-4">
                  {ann.content}
                </p>
                
                <div className="flex flex-wrap gap-2">
                  {ann.target_roles?.length > 0 ? (
                    ann.target_roles.map((role, idx) => (
                      <Badge key={idx} variant="secondary" className="capitalize text-[10px]">
                        {role}
                      </Badge>
                    ))
                  ) : (
                    <Badge variant="outline" className="text-[10px]">All Roles</Badge>
                  )}
                  
                  {ann.target_departments?.length > 0 && (
                    <Badge variant="outline" className="bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 text-[10px]">
                      {ann.target_departments.length} Department(s)
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
