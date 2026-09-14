import React, { createContext, useState, useEffect, useContext } from 'react';
import api from '../utils/api';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Verify token format/expiry first
          jwtDecode(token);
          
          // Fetch complete user data
          const res = await api.get('auth/me/');
          setUser(res.data.user);
        } catch (e) {
          console.error("Authentication failed during init", e);
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await api.post('auth/login/', { username, password });
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      
      const meRes = await api.get('auth/me/');
      setUser(meRes.data.user);
      
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (username, email, fullName, password, confirmPassword) => {
    try {
      await api.post('auth/register/', { 
        username, 
        email, 
        full_name: fullName, 
        password,
        confirm_password: confirmPassword 
      });
      return await login(username, password);
    } catch (error) {
      return { success: false, error: error.response?.data?.errors || 'Registration failed' };
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await api.post('auth/logout/', { refresh: refreshToken });
      }
    } catch (e) {
      console.error("Logout failed on server:", e);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, loading }}>
      {loading ? (
        <div className="flex h-screen w-screen items-center justify-center bg-forest-50 dark:bg-forest-950">
          <div className="text-forest-700 dark:text-forest-300 font-medium">Loading account...</div>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
