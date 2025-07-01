import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from './hooks/useAuth';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import SchedulingAgent from './pages/SchedulingAgent';
import Meetings from './pages/Meetings';
import Calendar from './pages/Calendar';
import Users from './pages/Users';
import Preferences from './pages/Preferences';
import OAuthCallback from './pages/OAuthCallback';

const AppRoutes: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (isAuthenticated && localStorage.getItem('auth_token')) {
    return (
      <>
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/scheduling-agent" element={<SchedulingAgent />} />
                <Route path="/meetings" element={<Meetings />} />
                <Route path="/calendar" element={<Calendar />} />
                <Route path="/users" element={<Users />} />
                <Route path="/preferences" element={<Preferences />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </motion.div>
          </main>
        </div>
      </>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/auth/callback/:provider" element={<OAuthCallback />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppRoutes />
    </div>
  );
};

export default App; 