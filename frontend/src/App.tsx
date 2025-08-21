import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import { motion } from 'framer-motion';

// Components
import Dashboard from './components/Dashboard';
import Login from './components/Login';

// Main App Component
const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);

  // Check authentication status
  React.useEffect(() => {
    const token = localStorage.getItem('auth_token');
    setIsAuthenticated(!!token);
  }, []);

  // Login handler
  const handleLogin = (token: string) => {
    localStorage.setItem('auth_token', token);
    setIsAuthenticated(true);
  };

  // Logout handler
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setIsAuthenticated(false);
  };

  return (
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <Routes>
          <Route
            path="/login"
            element={
              !isAuthenticated ? (
                <Login onLogin={handleLogin} />
              ) : (
                <Navigate to="/dashboard" replace />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <Dashboard onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route
            path="/"
            element={
              <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </motion.div>
    </Box>
  );
};

export default App;

