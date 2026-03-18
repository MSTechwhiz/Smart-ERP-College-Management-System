import React, { useState, useEffect } from 'react';
import { User, GraduationCap, Upload, Users, FileText, Home, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Label } from './label';
import { Textarea } from './textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from './dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs';
import { enhancedStudentAPI, departmentAPI } from '../../services/api';
import { toast } from 'sonner';
import { getYearLabel } from '../../lib/utils';

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
const PROGRAM_TYPES = [
  { value: 'B.E', label: 'B.E' },
  { value: 'B.Tech', label: 'B.Tech' },
  { value: 'MBA', label: 'MBA' },
  { value: 'MCA', label: 'MCA' }
];
const GENDERS = ['Male', 'Female', 'Other'];
const BOARDS = ['CBSE', 'State Board', 'ICSE', 'IB', 'Cambridge', 'Other'];
const ID_TYPES = ['aadhaar', 'pan', 'driving_license', 'voter_id', 'passport'];
const ADMISSION_TYPES = ['management', 'government', 'counselling'];
const COMMUNITIES = ['OC', 'BC', 'MBC', 'SC', 'ST', 'Other'];

export function EnhancedStudentForm({ isOpen, onClose, onSuccess, editStudent = null }) {
  const [activeTab, setActiveTab] = useState('basic');
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    // Basic Information
    name: '', email: '', password: '', roll_number: '', register_number: '',
    department_id: '', year: 1, semester: 1, section: '', batch: '',
    // Personal Details
    date_of_birth: '', gender: '', blood_group: '', mobile_number: '',
    alternate_mobile: '', program_type: '', program_duration: 0,
    permanent_address: '', communication_address: '',
    // 10th Certificate
    tenth_school_name: '', tenth_board: '', tenth_year: '',
    tenth_total_marks: '', tenth_marks_obtained: '', tenth_percentage: '',
    // 12th Certificate
    twelfth_school_name: '', twelfth_board: '', twelfth_year: '',
    twelfth_total_marks: '', twelfth_marks_obtained: '', twelfth_percentage: '', twelfth_cutoff: '',
    // Identity Proof
    id_type: '', id_number: '',
    // Additional
    community: '', scholarship_details: '', is_first_graduate: false,
    hostel_day_scholar: 'day_scholar', admission_type: '',
    admission_quota: '', emis_id: '', umis_id: '',
    // Parent Details
    parent_name: '', parent_phone: '',
    father_name: '', father_occupation: '', father_contact: '',
    mother_name: '', mother_occupation: '', mother_contact: '',
    guardian_name: '', guardian_contact: '',
    // Academic
    regulation: 'R2023', mentor_id: '',
  });

  useEffect(() => {
    loadDepartments();
    if (editStudent) {
      // Pre-fill form for editing
      setFormData(prev => ({
        ...prev,
        ...editStudent,
        tenth_school_name: editStudent.tenth_certificate?.school_name || '',
        tenth_board: editStudent.tenth_certificate?.board || '',
        tenth_year: editStudent.tenth_certificate?.year_of_passing || '',
        tenth_total_marks: editStudent.tenth_certificate?.total_marks || '',
        tenth_marks_obtained: editStudent.tenth_certificate?.marks_obtained || '',
        tenth_percentage: editStudent.tenth_certificate?.percentage || '',
        twelfth_school_name: editStudent.twelfth_certificate?.school_name || '',
        twelfth_board: editStudent.twelfth_certificate?.board || '',
        twelfth_year: editStudent.twelfth_certificate?.year_of_passing || '',
        twelfth_total_marks: editStudent.twelfth_certificate?.total_marks || '',
        twelfth_marks_obtained: editStudent.twelfth_certificate?.marks_obtained || '',
        twelfth_percentage: editStudent.twelfth_certificate?.percentage || '',
        twelfth_cutoff: editStudent.twelfth_certificate?.cutoff || '',
        id_type: editStudent.identity_proof?.id_type || '',
        id_number: editStudent.identity_proof?.id_number || '',
        father_name: editStudent.parent_details?.father_name || '',
        father_occupation: editStudent.parent_details?.father_occupation || '',
        father_contact: editStudent.parent_details?.father_contact || '',
        mother_name: editStudent.parent_details?.mother_name || '',
        mother_occupation: editStudent.parent_details?.mother_occupation || '',
        mother_contact: editStudent.parent_details?.mother_contact || '',
        guardian_name: editStudent.parent_details?.guardian_name || '',
        guardian_contact: editStudent.parent_details?.guardian_contact || '',
        admission_quota: editStudent.admission_quota || '',
        emis_id: editStudent.emis_id || '',
        umis_id: editStudent.umis_id || '',
        parent_name: editStudent.parent_name || '',
        parent_phone: editStudent.parent_phone || '',
      }));
    }
  }, [editStudent]);

  // ERP Logic: Auto-calculate fields
  useEffect(() => {
    if (!editStudent) {
      // 1. Program Duration
      let duration = 0;
      if (formData.program_type === 'B.E' || formData.program_type === 'B.Tech') {
        duration = 4;
      } else if (formData.program_type === 'MBA' || formData.program_type === 'MCA') {
        duration = 2;
      }

      if (duration !== formData.program_duration) {
        setFormData(prev => ({ ...prev, program_duration: duration }));
      }

      // 2. Year Calculation
      if (formData.batch && duration > 0) {
        const batchStart = parseInt(formData.batch.split('-')[0]);
        if (!isNaN(batchStart)) {
          const currentYear = new Date().getFullYear();
          const calculatedYear = Math.min(duration, Math.max(1, currentYear - batchStart + 1));
          if (calculatedYear !== parseInt(formData.year)) {
            setFormData(prev => ({ ...prev, year: String(calculatedYear) }));
          }
        }
      }
    }
  }, [formData.program_type, formData.batch, editStudent, formData.program_duration, formData.year]);

  const loadDepartments = async () => {
    try {
      const response = await departmentAPI.getAll();
      setDepartments(response.data);
    } catch (error) {
      console.error('Failed to load departments:', error);
    }
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const formatDateToISO = (dateStr) => {
    if (!dateStr) return null;
    // Handle dd-mm-yyyy or dd/mm/yyyy
    const parts = dateStr.split(/[-/]/);
    if (parts.length === 3) {
      const [day, month, year] = parts;
      if (year.length === 4) {
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
      }
      if (day.length === 4) { // Already yyyy-mm-dd
        return dateStr;
      }
    }
    return dateStr;
  };

  const handleSubmit = async () => {
    // Validation
    const requiredFields = ['name', 'email', 'register_number', 'department_id', 'batch', 'year', 'semester'];
    const missingFields = requiredFields.filter(f => !formData[f]);

    if (missingFields.length > 0) {
      toast.error('Please fill all required fields: ' + missingFields.join(', '));
      return;
    }

    if (!editStudent && !formData.password) {
      toast.error('Password is required for new students');
      return;
    }

    setLoading(true);
    try {
      // Prepare data for API
      const processedData = {
        ...formData,
        // Basic & Academic
        year: parseInt(formData.year) || 1,
        semester: parseInt(formData.semester) || 1,
        program_duration: parseInt(formData.program_duration) || 0,
        
        // 10th Certificate
        tenth_year: formData.tenth_year ? parseInt(formData.tenth_year) : null,
        tenth_total_marks: formData.tenth_total_marks ? parseFloat(formData.tenth_total_marks) : null,
        tenth_marks_obtained: formData.tenth_marks_obtained ? parseFloat(formData.tenth_marks_obtained) : null,
        tenth_percentage: formData.tenth_percentage ? parseFloat(formData.tenth_percentage) : null,
        
        // 12th Certificate
        twelfth_year: formData.twelfth_year ? parseInt(formData.twelfth_year) : null,
        twelfth_total_marks: formData.twelfth_total_marks ? parseFloat(formData.twelfth_total_marks) : null,
        twelfth_marks_obtained: formData.twelfth_marks_obtained ? parseFloat(formData.twelfth_marks_obtained) : null,
        twelfth_percentage: formData.twelfth_percentage ? parseFloat(formData.twelfth_percentage) : null,
        twelfth_cutoff: formData.twelfth_cutoff ? parseFloat(formData.twelfth_cutoff) : null,
        
        // Ensure contacts are strings
        mobile_number: formData.mobile_number ? String(formData.mobile_number) : '',
        alternate_mobile: formData.alternate_mobile ? String(formData.alternate_mobile) : '',
        parent_phone: formData.parent_phone ? String(formData.parent_phone) : '',
        father_contact: formData.father_contact ? String(formData.father_contact) : '',
        mother_contact: formData.mother_contact ? String(formData.mother_contact) : '',
        guardian_contact: formData.guardian_contact ? String(formData.guardian_contact) : '',
        
        date_of_birth: formatDateToISO(formData.date_of_birth)
      };

      if (editStudent) {
        await enhancedStudentAPI.updateProfile(editStudent.id, processedData);
        toast.success('Student updated successfully');
      } else {
        const form = new FormData();
        Object.entries(processedData).forEach(([key, value]) => {
          if (value !== '' && value !== null && value !== undefined) {
            form.append(key, value);
          }
        });
        await enhancedStudentAPI.create(form);
        toast.success('Student created successfully');
      }

      onSuccess?.();
      onClose();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save student');
    } finally {
      setLoading(false);
    }
  };

  const renderInput = (label, field, type = 'text', required = false, placeholder = '') => (
    <div className="space-y-1.5">
      <Label className="text-sm">
        {label} {required && <span className="text-destructive">*</span>}
      </Label>
      <Input
        type={type}
        value={formData[field] || ''}
        onChange={(e) => handleChange(field, e.target.value)}
        placeholder={placeholder}
        data-testid={`student-${field}`}
      />
    </div>
  );

  const renderSelect = (label, field, options, required = false) => (
    <div className="space-y-1.5">
      <Label className="text-sm">
        {label} {required && <span className="text-destructive">*</span>}
      </Label>
      <Select value={formData[field] || ''} onValueChange={(v) => handleChange(field, v)}>
        <SelectTrigger data-testid={`student-${field}`}>
          <SelectValue placeholder={`Select ${label.toLowerCase()}`} />
        </SelectTrigger>
        <SelectContent>
          {options.map(opt => (
            <SelectItem key={typeof opt === 'object' ? opt.value : opt} value={typeof opt === 'object' ? opt.value : opt}>
              {typeof opt === 'object' ? opt.label : opt}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <GraduationCap className="h-5 w-5" />
            {editStudent ? 'Edit Student Profile' : 'Add New Student'}
          </DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-5 w-full">
            <TabsTrigger value="basic" className="text-xs">
              <User className="h-3 w-3 mr-1" /> Basic Details
            </TabsTrigger>
            <TabsTrigger value="academic" className="text-xs">
              <GraduationCap className="h-3 w-3 mr-1" /> Academic
            </TabsTrigger>
            <TabsTrigger value="identity" className="text-xs">
              <FileText className="h-3 w-3 mr-1" /> Identity
            </TabsTrigger>
            <TabsTrigger value="parents" className="text-xs">
              <Users className="h-3 w-3 mr-1" /> Parents
            </TabsTrigger>
            <TabsTrigger value="additional" className="text-xs">
              <Home className="h-3 w-3 mr-1" /> Additional
            </TabsTrigger>
          </TabsList>

          {/* Basic Information */}
          <TabsContent value="basic" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Personal Information</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {renderInput('Full Name', 'name', 'text', true)}
                {renderInput('Email', 'email', 'email', true)}
                {!editStudent && renderInput('Password', 'password', 'password', true)}
                {renderSelect('Program Type', 'program_type', PROGRAM_TYPES, true)}
                <div className="space-y-1.5">
                  <Label className="text-sm text-muted-foreground">Student ID (System Generated)</Label>
                  <Input value={formData.roll_number || '(Auto Generated)'} disabled className="bg-muted font-mono" />
                </div>
                {renderInput('Roll Number', 'register_number', 'text', true, 'e.g., 2024CS001')}
                {renderSelect('Department', 'department_id', departments.map(d => ({ value: d.id, label: d.name })), true)}
                {renderInput('Batch', 'batch', 'text', true, 'e.g., 2020-2024')}
                {renderSelect('Year', 'year', Array.from({ length: formData.program_duration || 4 }, (_, i) => ({ value: String(i + 1), label: `Year ${i + 1}` })), true)}
                {renderSelect('Semester', 'semester',
                  formData.year ? [parseInt(formData.year) * 2 - 1, parseInt(formData.year) * 2].map(s => ({ value: String(s), label: `Semester ${s}` })) : []
                  , true)}
                {renderInput('Section', 'section', 'text', false, 'e.g., A')}
                {renderInput('Date of Birth', 'date_of_birth', 'date')}
                {renderSelect('Gender', 'gender', GENDERS)}
                {renderSelect('Blood Group', 'blood_group', BLOOD_GROUPS)}
                {renderInput('Mobile Number', 'mobile_number', 'tel')}
                {renderInput('Alternate Mobile', 'alternate_mobile', 'tel')}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Address</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label>Permanent Address</Label>
                  <Textarea
                    value={formData.permanent_address}
                    onChange={(e) => handleChange('permanent_address', e.target.value)}
                    rows={3}
                    data-testid="student-permanent-address"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label>Communication Address</Label>
                  <Textarea
                    value={formData.communication_address}
                    onChange={(e) => handleChange('communication_address', e.target.value)}
                    rows={3}
                    data-testid="student-communication-address"
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Academic Records */}
          <TabsContent value="academic" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">10th Certificate Details</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {renderInput('School Name', 'tenth_school_name')}
                {renderSelect('Board', 'tenth_board', BOARDS)}
                {renderInput('Year of Passing', 'tenth_year', 'number')}
                {renderInput('Total Marks', 'tenth_total_marks', 'number')}
                {renderInput('Marks Obtained', 'tenth_marks_obtained', 'number')}
                {renderInput('Percentage', 'tenth_percentage', 'number')}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">12th Certificate Details</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {renderInput('School Name', 'twelfth_school_name')}
                {renderSelect('Board', 'twelfth_board', BOARDS)}
                {renderInput('Year of Passing', 'twelfth_year', 'number')}
                {renderInput('Total Marks', 'twelfth_total_marks', 'number')}
                {renderInput('Marks Obtained', 'twelfth_marks_obtained', 'number')}
                {renderInput('Percentage', 'twelfth_percentage', 'number')}
                {renderInput('Cutoff', 'twelfth_cutoff', 'number', false, 'For Tamil Nadu students')}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Identity Proof */}
          <TabsContent value="identity" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Identity Proof</CardTitle>
                <CardDescription>Upload Aadhaar/PAN/Driving License</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderSelect('ID Type', 'id_type', ID_TYPES.map(t => ({ value: t, label: t.replace('_', ' ').toUpperCase() })))}
                {renderInput('ID Number', 'id_number')}
                {renderInput('EMIS ID', 'emis_id')}
                {renderInput('UMIS ID', 'umis_id')}
              </CardContent>
            </Card>
            <p className="text-sm text-muted-foreground">
              Note: Document upload will be available after creating the student profile.
            </p>
          </TabsContent>

          {/* Parent Details */}
          <TabsContent value="parents" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Father's Details</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {renderInput('Primary Parent Name', 'parent_name')}
                {renderInput('Primary Parent Contact', 'parent_phone', 'tel')}
                <div className="col-span-full border-t my-2 pt-2">
                  <p className="text-xs font-semibold text-slate-500 mb-4 uppercase tracking-wider text-center">Secondary Info (Traditional)</p>
                </div>
                {renderInput('Father\'s Name', 'father_name')}
                {renderInput('Occupation', 'father_occupation')}
                {renderInput('Contact Number', 'father_contact', 'tel')}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Mother's Details</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {renderInput('Mother\'s Name', 'mother_name')}
                {renderInput('Occupation', 'mother_occupation')}
                {renderInput('Contact Number', 'mother_contact', 'tel')}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Guardian Details (Optional)</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderInput('Guardian\'s Name', 'guardian_name')}
                {renderInput('Contact Number', 'guardian_contact', 'tel')}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Additional Information */}
          <TabsContent value="additional" className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Additional Information</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {renderSelect('Community', 'community', COMMUNITIES)}
                {renderInput('Scholarship Details', 'scholarship_details')}
                <div className="space-y-1.5">
                  <Label>First Graduate?</Label>
                  <Select
                    value={formData.is_first_graduate ? 'yes' : 'no'}
                    onValueChange={(v) => handleChange('is_first_graduate', v === 'yes')}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="yes">Yes</SelectItem>
                      <SelectItem value="no">No</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {renderSelect('Hostel/Day Scholar', 'hostel_day_scholar', [
                  { value: 'hostel', label: 'Hostel' },
                  { value: 'day_scholar', label: 'Day Scholar' }
                ])}
                {renderSelect('Admission Type', 'admission_type', ADMISSION_TYPES.map(t => ({ value: t, label: t.charAt(0).toUpperCase() + t.slice(1) })))}
                {renderSelect('Admission Quota', 'admission_quota', [
                  'Government quota', 'Management quota', '7.5 quota', 'PMSS', 'FG quota', 'MQ'
                ])}
                {renderInput('Regulation', 'regulation', 'text', false, 'e.g., R2023')}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={loading} data-testid="submit-student-btn">
            {loading ? 'Saving...' : (editStudent ? 'Update Student' : 'Create Student')}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

export default EnhancedStudentForm;
