import { useState } from 'react';
import { 
  TextField, 
  Button, 
  Box, 
  Typography, 
  Alert,
  Paper,
  Tab,
  Tabs,
  CircularProgress
} from '@mui/material';
import axios from 'axios';

function LoginForm({ setToken, setUser }) {
  const [tab, setTab] = useState(0);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
    setError('');
    setSuccess('');
  };

  const handleLogin = async () => {
    if (!username || !password) {
      setError('Username and password are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/login', {
        username,
        password
      });

      const { access_token, user } = response.data;
      
      // Store token in localStorage
      localStorage.setItem('token', access_token);
      
      // Set up axios defaults
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setToken(access_token);
      setUser(user);
      setSuccess('Login successful!');
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!username || !password) {
      setError('Username and password are required');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await axios.post('/api/register', {
        username,
        password,
        email: email || null
      });

      setSuccess('Registration successful! Please log in.');
      setTab(0); // Switch to login tab
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" textAlign="center" mb={3}>
        LinkOps-Afterlife
      </Typography>
      
      <Tabs value={tab} onChange={handleTabChange} centered sx={{ mb: 3 }}>
        <Tab label="Login" />
        <Tab label="Register" />
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
          fullWidth
          disabled={loading}
        />
        
        <TextField
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          fullWidth
          disabled={loading}
          helperText={tab === 1 ? "Minimum 8 characters" : ""}
        />
        
        {tab === 1 && (
          <TextField
            label="Email (optional)"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            fullWidth
            disabled={loading}
          />
        )}

        <Button
          variant="contained"
          onClick={tab === 0 ? handleLogin : handleRegister}
          disabled={loading}
          fullWidth
          sx={{ mt: 2 }}
        >
          {loading ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={20} />
              {tab === 0 ? 'Logging in...' : 'Registering...'}
            </Box>
          ) : (
            tab === 0 ? 'Login' : 'Register'
          )}
        </Button>
      </Box>

      <Typography variant="body2" textAlign="center" sx={{ mt: 3, color: 'text.secondary' }}>
        {tab === 0 
          ? "Don't have an account? Switch to Register tab." 
          : "Already have an account? Switch to Login tab."
        }
      </Typography>
    </Paper>
  );
}

export default LoginForm;