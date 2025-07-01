import React, { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { User } from '../types';

interface AuthContextType {
  currentUser: User | null;
  isAuthenticated: boolean;
  login: (user: User) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored user data on app load
    const storedUser = localStorage.getItem('current_user');
    const authToken = localStorage.getItem('auth_token');
    const currentPath = window.location.pathname;
    const isLoginPage = currentPath === '/login' || currentPath.startsWith('/auth/callback');
    if (!authToken && !isLoginPage) {
      setCurrentUser(null);
      localStorage.removeItem('current_user');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('oauth_state_google');
      localStorage.removeItem('oauth_state_github');
      window.location.replace('/login');
      return;
    }
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setCurrentUser(user);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        localStorage.removeItem('current_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = (user: User) => {
    setCurrentUser(user);
    localStorage.setItem('current_user', JSON.stringify(user));
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem('current_user');
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('oauth_state_google');
    localStorage.removeItem('oauth_state_github');
    // Add any other session keys here if needed
    window.location.replace('/login');
  };

  const value: AuthContextType = {
    currentUser,
    isAuthenticated: !!currentUser,
    login,
    logout,
    isLoading,
  };

  return React.createElement(AuthContext.Provider, { value }, children);
};