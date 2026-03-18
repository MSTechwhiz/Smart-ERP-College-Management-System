import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

// Helper to safely read/write user from localStorage
const getUserFromStorage = () => {
  try {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  // Initialize user directly from localStorage to avoid race condition
  const [user, setUser] = useState(getUserFromStorage);
  // If we already have a user in localStorage, skip the loading state
  const [loading, setLoading] = useState(!getUserFromStorage());

  const isAuthenticated = !!token && !!user;

  const fetchUser = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const response = await api.get('/auth/me');
      const userData = response.data;
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('role', userData.role);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('role');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Only call fetchUser on initial mount (when user is not cached)
  useEffect(() => {
    if (!getUserFromStorage() && token) {
      fetchUser();
    } else if (!token) {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only on mount

  const login = async (email, password, role) => {
    try {
      const response = await api.post('/auth/login', { email, password, role });
      const { access_token, user: userData } = response.data;

      // Store everything in localStorage for persistence
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('role', userData.role);

      setToken(access_token);
      setUser(userData);
      setLoading(false);

      console.log('Login success:', userData);
      console.log('Stored role:', userData.role);
      return { success: true, user: userData };
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed';
      return { success: false, error: message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('role');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    logout,
    refreshUser: fetchUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
