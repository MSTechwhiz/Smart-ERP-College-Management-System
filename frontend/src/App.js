import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import PrincipalDashboard from './pages/principal/PrincipalDashboard';
import AdminDashboard from './pages/admin/AdminDashboard';
import HODDashboard from './pages/hod/HODDashboard';
import FacultyDashboard from './pages/faculty/FacultyDashboard';
import StudentDashboard from './pages/student/StudentDashboard';
import MailboxPage from './pages/common/MailboxPage';
import AlertsPage from './pages/common/AlertsPage';
import AIChatbot from './components/ui/AIChatbot';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    return <Navigate to={`/${user?.role}`} replace />;
  }
  
  return children;
};

// Dashboard Router based on role
const DashboardRouter = () => {
  const { user } = useAuth();
  
  switch (user?.role) {
    case 'principal':
      return <Navigate to="/principal" replace />;
    case 'admin':
      return <Navigate to="/admin" replace />;
    case 'hod':
      return <Navigate to="/hod" replace />;
    case 'faculty':
      const dept = user?.department_code || 'dept';
      return <Navigate to={`/faculty/${dept}`} replace />;
    case 'student':
      return <Navigate to="/student" replace />;
    default:
      return <Navigate to="/" replace />;
  }
};

// Chatbot Wrapper - Only show when authenticated
const ChatbotWrapper = () => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return null;
  return <AIChatbot />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Toaster position="top-right" richColors closeButton />
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login/:role" element={<LoginPage />} />
          
          {/* Dashboard Router */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <DashboardRouter />
              </ProtectedRoute>
            } 
          />
          
          {/* Principal Routes */}
          <Route 
            path="/principal/*" 
            element={
              <ProtectedRoute allowedRoles={['principal']}>
                <PrincipalDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Admin Routes */}
          <Route 
            path="/admin/*" 
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* HOD Routes */}
          <Route 
            path="/hod/*" 
            element={
              <ProtectedRoute allowedRoles={['hod']}>
                <HODDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Faculty Routes */}
          <Route 
            path="/faculty/:deptCode/*" 
            element={
              <ProtectedRoute allowedRoles={['faculty']}>
                <FacultyDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Student Routes */}
          <Route 
            path="/student/*" 
            element={
              <ProtectedRoute allowedRoles={['student']}>
                <StudentDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Common Mailbox Route */}
          <Route 
            path="/mailbox" 
            element={
              <ProtectedRoute>
                <MailboxPage />
              </ProtectedRoute>
            } 
          />
          
          {/* Common Alerts Route */}
          <Route 
            path="/alerts" 
            element={
              <ProtectedRoute>
                <AlertsPage />
              </ProtectedRoute>
            } 
          />
          
          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        {/* Global AI Chatbot */}
        <ChatbotWrapper />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
