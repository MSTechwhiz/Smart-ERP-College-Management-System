import React, { useState, useEffect } from 'react';
import { History, Filter, Search, Download, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Button } from './button';
import { Input } from './input';
import { Label } from './label';
import { Badge } from './badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './select';
import { auditLogAPI } from '../../services/api';
import { toast } from 'sonner';

const MODULES = ['students', 'faculty', 'fees', 'attendance', 'marks', 'documents', 'grievances', 'announcements', 'subjects'];
const ACTIONS = ['create', 'update', 'delete', 'approve', 'reject', 'upload', 'bulk_insert'];
const ROLES = ['principal', 'admin', 'hod', 'faculty', 'student'];

export function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    module: '',
    action: '',
    role: '',
    start_date: '',
    end_date: '',
  });
  const [page, setPage] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const limit = 20;

  useEffect(() => {
    loadLogs();
  }, [page, filters]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        ...filters,
        skip: page * limit,
        limit,
      };
      // Remove empty values or 'all'
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === 'all' || params[key] === null || params[key] === undefined) delete params[key];
      });

      const response = await auditLogAPI.getAll(params);
      setLogs(response.data.logs || []);
      setTotal(response.data.total || 0);
    } catch (error) {
      toast.error('Failed to load audit logs');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const params = { ...filters };
      // Remove empty values or 'all'
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === 'all' || params[key] === null || params[key] === undefined) delete params[key];
      });

      const response = await auditLogAPI.export(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `audit_logs_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Audit logs exported successfully');
    } catch (error) {
      toast.error('Failed to export audit logs');
      console.error(error);
    }
  };

  const renderDetails = (log) => {
    if (log.details) return log.details;

    if (log.after_value) {
      const target = log.after_value.name || log.after_value.title || log.after_value.roll_number || log.target_id || '';
      return `${log.action} ${log.module}: ${target}`;
    }

    if (log.new_value) {
      return JSON.stringify(log.new_value).slice(0, 50) + '...';
    }

    return '-';
  };

  const handleFilterChange = (field, value) => {
    setFilters({ ...filters, [field]: value });
    setPage(0);
  };

  const clearFilters = () => {
    setFilters({
      module: '',
      action: '',
      role: '',
      start_date: '',
      end_date: '',
    });
    setPage(0);
  };

  const getActionColor = (action) => {
    const colors = {
      create: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      update: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
      delete: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      approve: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400',
      reject: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
      upload: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
      bulk_insert: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-400',
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <History className="h-8 w-8 text-primary" />
          <div>
            <h2 className="text-2xl font-bold">Audit Logs</h2>
            <p className="text-sm text-muted-foreground">Track all system activities</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Filter Logs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div className="space-y-1.5">
                <Label className="text-sm">Module</Label>
                <Select value={filters.module} onValueChange={(v) => handleFilterChange('module', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Modules" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Modules</SelectItem>
                    {MODULES.map(m => (
                      <SelectItem key={m} value={m} className="capitalize">{m}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1.5">
                <Label className="text-sm">Action</Label>
                <Select value={filters.action} onValueChange={(v) => handleFilterChange('action', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Actions" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Actions</SelectItem>
                    {ACTIONS.map(a => (
                      <SelectItem key={a} value={a} className="capitalize">{a.replace('_', ' ')}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1.5">
                <Label className="text-sm">Role</Label>
                <Select value={filters.role} onValueChange={(v) => handleFilterChange('role', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Roles" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Roles</SelectItem>
                    {ROLES.map(r => (
                      <SelectItem key={r} value={r} className="capitalize">{r}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1.5">
                <Label className="text-sm">Start Date</Label>
                <Input
                  type="date"
                  value={filters.start_date}
                  onChange={(e) => handleFilterChange('start_date', e.target.value)}
                />
              </div>

              <div className="space-y-1.5">
                <Label className="text-sm">End Date</Label>
                <Input
                  type="date"
                  value={filters.end_date}
                  onChange={(e) => handleFilterChange('end_date', e.target.value)}
                />
              </div>
            </div>
            <div className="flex justify-end mt-4">
              <Button variant="ghost" onClick={clearFilters}>Clear Filters</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Logs Table */}
      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <History className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No audit logs found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-sm">Timestamp</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">User</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Role</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Module</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Action</th>
                    <th className="text-left py-3 px-4 font-medium text-sm">Details</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4 text-sm">
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-sm font-medium">
                        {log.user_name}
                      </td>
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="capitalize">
                          {log.role}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm capitalize">
                        {log.module}
                      </td>
                      <td className="py-3 px-4">
                        <Badge className={`capitalize ${getActionColor(log.action)}`}>
                          {log.action.replace('_', ' ')}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground max-w-xs truncate">
                        {renderDetails(log)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {total > limit && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-sm text-muted-foreground">
                Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.max(0, p - 1))}
                  disabled={page === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm">
                  Page {page + 1} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                  disabled={page >= totalPages - 1}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default AuditLogs;
