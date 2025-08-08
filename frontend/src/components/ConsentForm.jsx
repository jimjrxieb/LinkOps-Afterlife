import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Checkbox,
  FormControlLabel,
  Typography,
  Box,
  Alert,
  Link,
  CircularProgress
} from '@mui/material';
import axios from 'axios';

function ConsentForm({ open, onClose, sessionId, onConsentGiven }) {
  const [consents, setConsents] = useState({
    terms_agreed: false,
    data_processing_agreed: false,
    emotional_impact_acknowledged: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleConsentChange = (consentType) => (event) => {
    setConsents(prev => ({
      ...prev,
      [consentType]: event.target.checked
    }));
  };

  const allConsentsGiven = Object.values(consents).every(consent => consent);

  const handleSubmit = async () => {
    if (!allConsentsGiven) {
      setError('All consent agreements are required to proceed.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await axios.post(`/api/consent/${sessionId}`, {
        ...consents,
        user_agent: navigator.userAgent,
        ip_address: 'client_side' // Will be determined server-side
      });

      onConsentGiven();
      onClose();
      
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to submit consent. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={!loading ? onClose : undefined}
      maxWidth="md" 
      fullWidth
      disableEscapeKeyDown={loading}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Typography variant="h5" component="div">
          Consent Agreement Required
        </Typography>
        <Typography variant="subtitle2" color="text.secondary">
          LinkOps-Afterlife Digital Memorial Platform
        </Typography>
      </DialogTitle>
      
      <DialogContent sx={{ py: 2 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            This platform creates digital memorials to honor deceased loved ones. 
            Please read and agree to the following terms before proceeding.
          </Typography>
        </Alert>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Terms of Use and Data Processing
          </Typography>
          
          <FormControlLabel
            control={
              <Checkbox
                checked={consents.terms_agreed}
                onChange={handleConsentChange('terms_agreed')}
                disabled={loading}
              />
            }
            label={
              <Typography variant="body2">
                I agree to the Terms of Use and understand that this platform:
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  <li>Creates AI-generated content based on uploaded materials</li>
                  <li>Uses third-party APIs (D-ID, ElevenLabs) for processing</li>
                  <li>Stores data securely with encryption</li>
                  <li>Is intended for memorial and remembrance purposes only</li>
                </ul>
              </Typography>
            }
            sx={{ alignItems: 'flex-start', mb: 2 }}
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={consents.data_processing_agreed}
                onChange={handleConsentChange('data_processing_agreed')}
                disabled={loading}
              />
            }
            label={
              <Typography variant="body2">
                I consent to the processing of uploaded data (photos, audio, text) for:
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  <li>AI avatar generation and voice cloning</li>
                  <li>Personality analysis and conversation modeling</li>
                  <li>Temporary storage during processing</li>
                  <li>Secure deletion upon request</li>
                </ul>
              </Typography>
            }
            sx={{ alignItems: 'flex-start', mb: 2 }}
          />

          <FormControlLabel
            control={
              <Checkbox
                checked={consents.emotional_impact_acknowledged}
                onChange={handleConsentChange('emotional_impact_acknowledged')}
                disabled={loading}
              />
            }
            label={
              <Typography variant="body2">
                I acknowledge the emotional nature of this technology and understand:
                <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
                  <li>This is a digital simulation, not the actual person</li>
                  <li>Interactions may evoke strong emotional responses</li>
                  <li>Professional grief counseling is recommended if needed</li>
                  <li>I can delete all data at any time</li>
                </ul>
              </Typography>
            }
            sx={{ alignItems: 'flex-start', mb: 2 }}
          />
        </Box>

        <Box sx={{ p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>Privacy Notice:</strong> Your data is encrypted and stored securely. 
            You can request complete deletion at any time. For grief support resources, 
            visit <Link href="https://www.griefshare.org/" target="_blank" rel="noopener">
              GriefShare.org
            </Link>.
          </Typography>
        </Box>
      </DialogContent>
      
      <DialogActions sx={{ p: 3, pt: 1 }}>
        <Button 
          onClick={onClose} 
          disabled={loading}
          color="secondary"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!allConsentsGiven || loading}
          variant="contained"
          color="primary"
        >
          {loading ? (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <CircularProgress size={20} />
              Submitting...
            </Box>
          ) : (
            'I Agree and Consent'
          )}
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ConsentForm;