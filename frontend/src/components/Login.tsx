import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Container,
  Alert,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

interface LoginProps {
  onLogin: (token: string) => void;
}

interface LoginForm {
  email: string;
  password: string;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>();

  const onSubmit = async (data: LoginForm) => {
    setLoading(true);
    setError('');

    try {
      // Mock authentication - replace with real API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (data.email === 'admin@cryptoanalyzer.com' && data.password === 'admin123') {
        const mockToken = 'mock-jwt-token-' + Date.now();
        onLogin(mockToken);
        toast.success('Login successful!');
      } else {
        throw new Error('Invalid credentials');
      }
    } catch (err) {
      setError('Invalid email or password');
      toast.error('Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          style={{ width: '100%' }}
        >
          <Card sx={{ p: 4 }}>
            <CardContent>
              <Box sx={{ textAlign: 'center', mb: 4 }}>
                <Typography variant="h3" component="h1" gutterBottom>
                  📊 CryptoAnalyzer Pro
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  Advanced Cryptocurrency Analysis Platform
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 3 }}>
                  {error}
                </Alert>
              )}

              <Box
                component="form"
                onSubmit={handleSubmit(onSubmit)}
                sx={{ mt: 2 }}
              >
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  margin="normal"
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: 'Invalid email address',
                    },
                  })}
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  disabled={loading}
                />

                <TextField
                  fullWidth
                  label="Password"
                  type="password"
                  margin="normal"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters',
                    },
                  })}
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  disabled={loading}
                />

                <Button
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  sx={{ mt: 3, mb: 2, py: 1.5 }}
                >
                  {loading ? (
                    <CircularProgress size={24} color="inherit" />
                  ) : (
                    'Sign In'
                  )}
                </Button>
              </Box>

              <Box sx={{ mt: 4, p: 2, backgroundColor: 'action.hover', borderRadius: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  <strong>Demo Credentials:</strong>
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Email: admin@cryptoanalyzer.com
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Password: admin123
                </Typography>
              </Box>

              <Box sx={{ mt: 3, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  CryptoAnalyzer Pro v1.0.0 - Fixed Version
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Container>
  );
};

export default Login;

