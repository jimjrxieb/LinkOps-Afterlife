import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Card,
  CardContent,
  Divider,
  Chip,
  Stack,
  LinearProgress,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Person,
  Save,
  Info,
  Psychology,
  Family,
  Work,
  LocationOn,
  Sports,
  Clear
} from '@mui/icons-material';
import axios from 'axios';

const BioForm = ({ sessionId, onBioSubmitted, onClose }) => {
  const [whoAmI, setWhoAmI] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showExamples, setShowExamples] = useState(true);

  const characterCount = whoAmI.length;
  const maxLength = 10000;
  const isOverLimit = characterCount > maxLength;

  const handleSubmit = async () => {
    if (!whoAmI.trim()) {
      setError('Please enter some biographical information');
      return;
    }

    if (isOverLimit) {
      setError(`Biography is too long. Please keep it under ${maxLength} characters.`);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const response = await axios.post(`/api/fine_tune_bio/${sessionId}`, {
        who_am_i: whoAmI.trim()
      });

      setSuccess(true);
      
      if (onBioSubmitted) {
        onBioSubmitted(response.data);
      }

      // Auto-close after success
      setTimeout(() => {
        if (onClose) {
          onClose();
        }
      }, 2000);

    } catch (err) {
      console.error('Bio submission error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to submit biographical information. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const examplePrompts = [
    {
      icon: Person,
      title: "Identity & Nicknames",
      examples: ["Call me Sis", "Everyone knows me as Tommy", "My nickname is Ace"]
    },
    {
      icon: Family,  
      title: "Family & Relationships",
      examples: ["My mom is Jane, dad is Bob", "I have 2 kids: Alex and Mia", "My brother Sam lives in Chicago"]
    },
    {
      icon: Work,
      title: "Profession & Work",
      examples: ["I work as a barber", "I'm a teacher at Lincoln High", "I run my own restaurant"]
    },
    {
      icon: LocationOn,
      title: "Background & Locations", 
      examples: ["I grew up in NYC", "Born and raised in Texas", "Moved to California in 2010"]
    },
    {
      icon: Psychology,
      title: "Personality Traits",
      examples: ["I'm known for being funny and caring", "People say I'm stubborn but loyal", "I'm the organized one in the family"]
    },
    {
      icon: Sports,
      title: "Hobbies & Interests",
      examples: ["I love playing guitar", "I'm obsessed with cooking", "I play basketball every weekend"]
    }
  ];

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Box display="flex" alignItems="center" mb={3}>
        <Person color="primary" sx={{ mr: 2, fontSize: '2rem' }} />
        <Box flexGrow={1}>
          <Typography variant="h4" component="h1" gutterBottom>
            Who Am I? 
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Share personal details to make your avatar more authentic and personalized
          </Typography>
        </Box>
        {onClose && (
          <IconButton onClick={onClose} size="large">
            <Clear />
          </IconButton>
        )}
      </Box>

      <Divider sx={{ mb: 3 }} />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Biographical information saved successfully! Your avatar will now have enhanced personality context.
        </Alert>
      )}

      {/* Example prompts */}
      {showExamples && (
        <Card variant="outlined" sx={{ mb: 3, bgcolor: 'grey.50' }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Info color="info" sx={{ mr: 1 }} />
              <Typography variant="h6" component="h3">
                What to Include
              </Typography>
              <Button 
                size="small" 
                onClick={() => setShowExamples(false)}
                sx={{ ml: 'auto' }}
              >
                Hide Examples
              </Button>
            </Box>
            
            <Typography variant="body2" color="text.secondary" mb={2}>
              Help your avatar understand who you are by sharing details like:
            </Typography>

            <Stack spacing={2}>
              {examplePrompts.map((prompt, index) => {
                const IconComponent = prompt.icon;
                return (
                  <Box key={index}>
                    <Box display="flex" alignItems="center" mb={1}>
                      <IconComponent color="primary" sx={{ mr: 1, fontSize: '1.2rem' }} />
                      <Typography variant="subtitle2" fontWeight="bold">
                        {prompt.title}
                      </Typography>
                    </Box>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {prompt.examples.map((example, exampleIndex) => (
                        <Chip
                          key={exampleIndex}
                          label={example}
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            const newText = whoAmI + (whoAmI ? '\n' : '') + example;
                            if (newText.length <= maxLength) {
                              setWhoAmI(newText);
                            }
                          }}
                          sx={{ mb: 0.5, cursor: 'pointer' }}
                        />
                      ))}
                    </Stack>
                  </Box>
                );
              })}
            </Stack>
          </CardContent>
        </Card>
      )}

      {/* Main bio input */}
      <Box mb={3}>
        <TextField
          multiline
          rows={8}
          fullWidth
          variant="outlined"
          label="Tell us about yourself..."
          placeholder="Share details that make you unique: nicknames, family members, your job, where you're from, your personality, hobbies, and anything else that defines who you are.

Example: 'Call me Sis - I'm a barber from NYC with 2 kids named Alex and Mia. My mom is Jane and dad is Bob. People say I'm funny and caring but stubborn sometimes. I love playing guitar and cooking for my family. My brother Sam visits from Chicago every summer.'"
          value={whoAmI}
          onChange={(e) => setWhoAmI(e.target.value)}
          error={isOverLimit}
          helperText={
            <Box display="flex" justifyContent="space-between">
              <span>This information helps create more authentic, personalized conversations</span>
              <span style={{ color: isOverLimit ? 'red' : 'inherit' }}>
                {characterCount} / {maxLength} characters
              </span>
            </Box>
          }
          disabled={submitting}
        />
        
        {submitting && (
          <Box mt={2}>
            <Typography variant="body2" gutterBottom>
              Saving biographical information...
            </Typography>
            <LinearProgress />
          </Box>
        )}
      </Box>

      {/* Action buttons */}
      <Box display="flex" justifyContent="center" gap={2}>
        <Button
          variant="contained"
          size="large"
          onClick={handleSubmit}
          disabled={submitting || !whoAmI.trim() || isOverLimit}
          startIcon={<Save />}
          sx={{ minWidth: 200, py: 1.5 }}
        >
          {submitting ? 'Saving...' : 'Save Biography'}
        </Button>
        
        {onClose && (
          <Button
            variant="outlined"
            size="large"
            onClick={onClose}
            disabled={submitting}
            sx={{ minWidth: 100, py: 1.5 }}
          >
            Cancel
          </Button>
        )}
      </Box>

      {/* Footer note */}
      <Box mt={3}>
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Privacy & Security:</strong> Your biographical information is encrypted and stored securely. 
            It will be used exclusively to enhance your avatar's personality and conversation authenticity.
          </Typography>
        </Alert>
      </Box>
    </Paper>
  );
};

export default BioForm;