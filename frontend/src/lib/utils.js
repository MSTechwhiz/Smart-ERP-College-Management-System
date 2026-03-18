import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatDate(date) {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

export function formatDateTime(date) {
  if (!date) return '';
  const d = new Date(date);
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

export function formatCurrency(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

export function getGradeColor(grade) {
  const colors = {
    'O': 'text-emerald-600 bg-emerald-100',
    'A+': 'text-emerald-600 bg-emerald-100',
    'A': 'text-blue-600 bg-blue-100',
    'B+': 'text-blue-600 bg-blue-100',
    'B': 'text-amber-600 bg-amber-100',
    'C': 'text-amber-600 bg-amber-100',
    'P': 'text-orange-600 bg-orange-100',
    'F': 'text-rose-600 bg-rose-100',
  };
  return colors[grade] || 'text-slate-600 bg-slate-100';
}

export function getRiskColor(level) {
  const colors = {
    'high': 'text-rose-600 bg-rose-100',
    'medium': 'text-amber-600 bg-amber-100',
    'low': 'text-emerald-600 bg-emerald-100',
  };
  return colors[level] || 'text-slate-600 bg-slate-100';
}

export function getStatusColor(status) {
  const colors = {
    'completed': 'text-emerald-600 bg-emerald-100',
    'pending': 'text-amber-600 bg-amber-100',
    'failed': 'text-rose-600 bg-rose-100',
    'submitted': 'text-blue-600 bg-blue-100',
    'approved': 'text-emerald-600 bg-emerald-100',
    'rejected': 'text-rose-600 bg-rose-100',
    'open': 'text-blue-600 bg-blue-100',
    'resolved': 'text-emerald-600 bg-emerald-100',
    'in_progress': 'text-amber-600 bg-amber-100',
    'faculty_review': 'text-blue-600 bg-blue-100',
    'hod_review': 'text-amber-600 bg-amber-100',
    'Pending': 'text-amber-600 bg-amber-100',
    'Verified': 'text-blue-600 bg-blue-100',
    'Approved': 'text-emerald-600 bg-emerald-100',
    'Signed': 'text-indigo-600 bg-indigo-100',
    'Issued': 'text-purple-600 bg-purple-100',
    'Rejected': 'text-rose-600 bg-rose-100',
  };
  return colors[status] || 'text-slate-600 bg-slate-100';
}
export function getYearLabel(semester) {
  const sem = parseInt(semester);
  if (sem === 1 || sem === 2) return "1st Year";
  if (sem === 3 || sem === 4) return "2nd Year";
  if (sem === 5 || sem === 6) return "3rd Year";
  if (sem === 7 || sem === 8) return "Final Year";
  return "N/A";
}
