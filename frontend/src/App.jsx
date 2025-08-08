import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Paper,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Chip,
  Divider,
  IconButton,
  Menu,
  MenuItem
} from '@mui/material';
import {
  CloudUpload,
  Settings,
  Chat,
  History,
  Warning,
  AccountCircle,
  Delete,
  ExitToApp
} from '@mui/icons-material';
import axios from 'axios';

// Import components
import UploadForm from './components/UploadForm';
import ProcessingStatus from './components/ProcessingStatus';
import InteractionPanel from './components/InteractionPanel';
import SessionHistory from './components/SessionHistory';
import LoginForm from './components/LoginForm.jsx';
import ConsentForm from './components/ConsentForm.jsx';
import BioForm from './components/BioForm.jsx';

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8000';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
    },
    h4: {
      fontSize: '1.8rem',
      fontWeight: 500,
    },
  },
});

const steps = [
  { label: 'Upload Files', icon: CloudUpload },
  { label: 'Process Data', icon: Settings },
  { label: 'Interact', icon: Chat },
  { label: 'History', icon: History }
];

function App() {
  const [activeStep, setActiveStep] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [sessionData, setSessionData] = useState(null);
  const [ethicsDialog, setEthicsDialog] = useState(true);
  const [serverStatus, setServerStatus] = useState(null);
  
  // Authentication state
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  
  // Consent state
  const [consentDialog, setConsentDialog] = useState(false);
  const [consentGiven, setConsentGiven] = useState(false);
  
  // Bio state
  const [bioDialog, setBioDialog] = useState(false);
  const [bioProvided, setBioProvided] = useState(false);

  useEffect(() => {
    checkServerStatus();
    
    // Check if token exists and set up axios
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  const checkServerStatus = async () => {
    try {
      const response = await axios.get('/ping');
      setServerStatus({ status: 'online', data: response.data });
    } catch (err) {
      setServerStatus({ 
        status: 'offline', 
        error: err.message || 'Server unreachable' 
      });
    }
  };

  const handleUploadSuccess = (data) => {
    setSessionData(data);
    setSessionId(data.session_id);
    setConsentDialog(true); // Show consent dialog after upload
  };

  const handleConsentGiven = () => {
    setConsentGiven(true);
    setBioDialog(true); // Show bio dialog after consent
  };

  const handleBioSubmitted = (data) => {
    setBioProvided(true);
    setBioDialog(false);
    setActiveStep(1); // Proceed to processing after bio
  };

  const handleBioSkipped = () => {
    setBioDialog(false);
    setActiveStep(1); // Proceed to processing without bio
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    setSessionId(null);
    setSessionData(null);
    setConsentGiven(false);
    setBioProvided(false);
    setActiveStep(0);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUserMenuAnchor(null);
  };

  const handleDeleteSession = async () => {
    if (!sessionId) return;
    
    try {
      await axios.delete(`/api/delete_session/${sessionId}`);
      setSessionId(null);
      setSessionData(null);
      setConsentGiven(false);
      setBioProvided(false);
      setActiveStep(0);
      setUserMenuAnchor(null);
      alert('Session deleted successfully');
    } catch (error) {
      alert(error.response?.data?.detail || 'Failed to delete session');
    }
  };

  const handleProcessingComplete = () => {
    setActiveStep(2);
  };

  const handleStepClick = (step) => {
    // Only allow clicking on completed steps or the next available step
    if (step <= activeStep || (step === 1 && sessionId)) {
      setActiveStep(step);
    }
  };

  const renderStepContent = () => {
    if (!token) {
      return <LoginForm setToken={setToken} setUser={setUser} />;
    }

    if (!consentGiven && sessionId) {
      return (
        <Alert severity="info">
          Please complete the consent process to continue.
        </Alert>
      );
    }

    if (bioDialog) {
      return (
        <BioForm
          sessionId={sessionId}
          onBioSubmitted={handleBioSubmitted}
          onClose={handleBioSkipped}
        />
      );
    }

    switch (activeStep) {
      case 0:
        return (
          <UploadForm
            onUploadSuccess={handleUploadSuccess}
            onSessionStart={setSessionId}
          />
        );
      
      case 1:
        return sessionId && consentGiven ? (
          <ProcessingStatus
            sessionId={sessionId}
            onProcessingComplete={handleProcessingComplete}
          />
        ) : (
          <Alert severity="warning">
            Please upload files and complete consent to proceed with processing.
          </Alert>
        );
      
      case 2:
        return sessionId && consentGiven ? (
          <InteractionPanel sessionId={sessionId} />
        ) : (
          <Alert severity="warning">
            Please complete the upload and processing steps first.
          </Alert>
        );
      
      case 3:
        return sessionId && consentGiven ? (
          <SessionHistory sessionId={sessionId} />
        ) : (
          <Alert severity="warning">
            Please complete previous steps to view interaction history.
          </Alert>
        );
      
      default:
        return <div>Unknown step</div>;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      
      {/* App Bar */}
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            LinkOps-Afterlife
          </Typography>
          
          <Box display="flex" alignItems="center" gap={2}>
            {sessionId && (
              <Chip
                label={`Session: ${sessionId.slice(0, 8)}...`}
                variant="outlined"
                size="small"
                sx={{ color: 'white', borderColor: 'white' }}
              />
            )}
            
            <Chip
              label={serverStatus?.status === 'online' ? 'Server Online' : 'Server Offline'}
              color={serverStatus?.status === 'online' ? 'success' : 'error'}
              size="small"
              variant="outlined"
              sx={{ color: 'white', borderColor: 'white' }}
            />

            {token && user && (
              <>
                <IconButton
                  color="inherit"
                  onClick={(e) => setUserMenuAnchor(e.currentTarget)}
                >
                  <AccountCircle />
                </IconButton>
                <Menu
                  anchorEl={userMenuAnchor}
                  open={Boolean(userMenuAnchor)}
                  onClose={() => setUserMenuAnchor(null)}
                >
                  <MenuItem disabled>
                    <Typography variant="body2">
                      {user.username}
                    </Typography>
                  </MenuItem>
                  {sessionId && (
                    <MenuItem onClick={handleDeleteSession}>
                      <Delete sx={{ mr: 1 }} />
                      Delete Session
                    </MenuItem>
                  )}
                  <MenuItem onClick={handleLogout}>
                    <ExitToApp sx={{ mr: 1 }} />
                    Logout
                  </MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Server Status Alert */}
        {serverStatus?.status === 'offline' && (
          <Alert severity="error" sx={{ mb: 3 }}>
            Server is currently offline. Please ensure the backend is running on port 8000.
            <Button onClick={checkServerStatus} sx={{ ml: 2 }}>
              Retry Connection
            </Button>
          </Alert>
        )}

        {/* Progress Stepper - Only show when authenticated */}
        {token && (
          <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
            <Stepper activeStep={activeStep} alternativeLabel>
              {steps.map((step, index) => {
                const StepIcon = step.icon;
                return (
                  <Step 
                    key={step.label}
                    sx={{ cursor: 'pointer' }}
                    onClick={() => handleStepClick(index)}
                  >
                    <StepLabel
                      StepIconComponent={() => (
                        <Box
                          sx={{
                            width: 40,
                            height: 40,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            bgcolor: index <= activeStep ? 'primary.main' : 'grey.300',
                            color: index <= activeStep ? 'white' : 'grey.600',
                            cursor: 'pointer'
                          }}
                        >
                          <StepIcon />
                        </Box>
                      )}
                    >
                      {step.label}
                    </StepLabel>
                  </Step>
                );
              })}
            </Stepper>
          </Paper>
        )}

        {/* Step Content */}
        <Box>
          {renderStepContent()}
        </Box>

        {/* Navigation Buttons - Only show when authenticated and stepped through */}
        {token && activeStep > 0 && (
          <Box display="flex" justifyContent="space-between" mt={4}>
            <Button
              onClick={() => setActiveStep(activeStep - 1)}
              variant="outlined"
            >
              Back
            </Button>
            
            {activeStep < steps.length - 1 && (
              <Button
                onClick={() => setActiveStep(activeStep + 1)}
                variant="contained"
                disabled={!sessionId || !consentGiven}
              >
                Next
              </Button>
            )}
          </Box>
        )}
      </Container>

      {/* Consent Form Dialog */}
      <ConsentForm
        open={consentDialog}
        onClose={() => setConsentDialog(false)}
        sessionId={sessionId}
        onConsentGiven={handleConsentGiven}
      />

      {/* Ethics and Privacy Dialog */}
      <Dialog
        open={ethicsDialog}
        onClose={() => setEthicsDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <Warning color="warning" sx={{ mr: 1 }} />
            Important: Ethics & Privacy Notice
          </Box>
        </DialogTitle>
        <DialogContent>
          <DialogContentText component="div">
            <Typography variant="h6" gutterBottom>
              Digital Afterlife Technology
            </Typography>
            
            <Typography paragraph>
              LinkOps-Afterlife creates AI-powered digital representations of individuals 
              using their photos, voice recordings, and text communications. This technology 
              is designed to help preserve memories and enable meaningful interactions.
            </Typography>

            <Typography variant="h6" gutterBottom>
              Ethical Considerations
            </Typography>
            
            <Box component="ul" sx={{ pl: 2 }}>
              <Typography component="li" paragraph>
                <strong>Consent:</strong> Only use materials from individuals who have given 
                explicit consent for their digital representation.
              </Typography>
              
              <Typography component="li" paragraph>
                <strong>Respect:</strong> This technology should be used to honor and remember 
                individuals in a respectful manner.
              </Typography>
              
              <Typography component="li" paragraph>
                <strong>Privacy:</strong> All uploaded data is processed locally and securely. 
                No data is shared with external parties without consent.
              </Typography>
              
              <Typography component="li" paragraph>
                <strong>Emotional Wellbeing:</strong> Please consider the emotional impact on 
                yourself and others when interacting with digital representations.
              </Typography>
            </Box>

            <Typography variant="h6" gutterBottom>
              Data Processing
            </Typography>
            
            <Typography paragraph>
              Your uploaded files will be processed using AI/ML technologies including:
            </Typography>
            
            <Box component="ul" sx={{ pl: 2 }}>
              <Typography component="li">Computer vision for image processing</Typography>
              <Typography component="li">Voice cloning for speech synthesis</Typography>
              <Typography component="li">Natural language processing for personality analysis</Typography>
              <Typography component="li">Avatar generation for video responses</Typography>
            </Box>

            <Divider sx={{ my: 2 }} />
            
            <Typography variant="body2" color="text.secondary">
              By continuing, you acknowledge that you understand these considerations 
              and agree to use this technology responsibly and ethically.
            </Typography>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEthicsDialog(false)} color="primary" variant="contained">
            I Understand and Agree
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bio Dialog for Optional Biographical Information */}
      <Dialog
        open={bioDialog}
        onClose={handleBioSkipped}
        maxWidth="md"
        fullWidth
      >
        <BioForm
          sessionId={sessionId}
          onBioSubmitted={handleBioSubmitted}
          onClose={handleBioSkipped}
        />
      </Dialog>
    </ThemeProvider>
  );
}

export default App;