import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Card,
  CardContent,
  LinearProgress,
  Divider,
  Collapse,
  IconButton
} from '@mui/material';
import {
  CheckCircle,
  Error,
  PlayArrow,
  Refresh,
  ExpandMore,
  ExpandLess,
  Photo,
  RecordVoiceOver,
  TextFields,
  Psychology,
  SmartToy
} from '@mui/icons-material';
import axios from 'axios';

const ProcessingStatus = ({ sessionId, onProcessingComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [stepStatus, setStepStatus] = useState({});
  const [stepDetails, setStepDetails] = useState({});
  const [expandedSteps, setExpandedSteps] = useState({});
  const [sessionStatus, setSessionStatus] = useState(null);

  const processingSteps = [
    {
      id: 'preprocess_photo',
      label: 'Photo Preprocessing',
      description: 'Analyzing and enhancing the uploaded photo for avatar generation',
      icon: Photo,
      endpoint: `/api/preprocess_photo/${sessionId}`,
      method: 'GET'
    },
    {
      id: 'clone_voice',
      label: 'Voice Cloning',
      description: 'Creating a unique voice model from the uploaded audio',
      icon: RecordVoiceOver,
      endpoint: `/api/clone_voice/${sessionId}`,
      method: 'POST'
    },
    {
      id: 'process_text',
      label: 'Text Analysis',
      description: 'Analyzing personality traits and communication patterns',
      icon: TextFields,
      endpoint: `/api/process_text/${sessionId}`,
      method: 'POST'
    },
    {
      id: 'fine_tune_conversation',
      label: 'Conversation Model',
      description: 'Fine-tuning the conversational AI based on personality analysis',
      icon: Psychology,
      endpoint: `/api/fine_tune_conversation/${sessionId}`,
      method: 'POST'
    }
  ];

  useEffect(() => {
    if (sessionId) {
      checkSessionStatus();
    }
  }, [sessionId]);

  const checkSessionStatus = async () => {
    try {
      const response = await axios.get(`/api/session_status/${sessionId}`);
      setSessionStatus(response.data);
      
      // Update step status based on session requirements
      const requirements = response.data.session_requirements || {};
      const newStepStatus = {};
      
      if (requirements.preprocessed_photo?.exists) {
        newStepStatus.preprocess_photo = 'completed';
      }
      if (requirements.voice_metadata?.exists) {
        newStepStatus.clone_voice = 'completed';
      }
      if (requirements.conversation_model?.exists) {
        newStepStatus.process_text = 'completed';
        newStepStatus.fine_tune_conversation = 'completed';
      }
      
      setStepStatus(newStepStatus);
    } catch (err) {
      console.error('Error checking session status:', err);
    }
  };

  const processStep = async (step) => {
    setProcessing(true);
    setError(null);
    setStepStatus(prev => ({ ...prev, [step.id]: 'processing' }));

    try {
      const response = await axios({
        method: step.method,
        url: step.endpoint,
        data: step.method === 'POST' ? {} : undefined
      });

      setStepStatus(prev => ({ ...prev, [step.id]: 'completed' }));
      setStepDetails(prev => ({ ...prev, [step.id]: response.data }));
      
      // Auto-expand completed step
      setExpandedSteps(prev => ({ ...prev, [step.id]: true }));
      
      // Move to next step
      const currentIndex = processingSteps.findIndex(s => s.id === step.id);
      if (currentIndex < processingSteps.length - 1) {
        setActiveStep(currentIndex + 1);
      } else {
        // All steps completed
        if (onProcessingComplete) {
          onProcessingComplete();
        }
      }
    } catch (err) {
      console.error(`Error processing ${step.id}:`, err);
      setStepStatus(prev => ({ ...prev, [step.id]: 'error' }));
      setError(err.response?.data?.detail || `Failed to ${step.label.toLowerCase()}`);
    } finally {
      setProcessing(false);
    }
  };

  const processAllSteps = async () => {
    for (const step of processingSteps) {
      if (stepStatus[step.id] !== 'completed') {
        await processStep(step);
        if (stepStatus[step.id] === 'error') break;
      }
    }
  };

  const toggleStepExpansion = (stepId) => {
    setExpandedSteps(prev => ({
      ...prev,
      [stepId]: !prev[stepId]
    }));
  };

  const getStepIcon = (step, status) => {
    const IconComponent = step.icon;
    
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'processing':
        return <CircularProgress size={24} />;
      case 'error':
        return <Error color="error" />;
      default:
        return <IconComponent color="action" />;
    }
  };

  const getStepColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'primary';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const renderStepDetails = (step, details) => {
    if (!details) return null;

    switch (step.id) {
      case 'preprocess_photo':
        return (
          <Box>
            <Typography variant="body2" gutterBottom>
              <strong>Image Info:</strong>
            </Typography>
            <Typography variant="caption" display="block">
              Size: {details.image_info?.width} x {details.image_info?.height}
            </Typography>
            <Typography variant="caption" display="block">
              Format: {details.image_info?.format}
            </Typography>
          </Box>
        );
      
      case 'clone_voice':
        return (
          <Box>
            <Typography variant="body2" gutterBottom>
              <strong>Voice Model:</strong>
            </Typography>
            <Typography variant="caption" display="block">
              Voice ID: {details.voice_id}
            </Typography>
            <Typography variant="caption" display="block">
              Quality: {details.voice_metadata?.quality || 'High'}
            </Typography>
          </Box>
        );
      
      case 'process_text':
        return (
          <Box>
            <Typography variant="body2" gutterBottom>
              <strong>Analysis Summary:</strong>
            </Typography>
            <Typography variant="caption" display="block">
              Dominant Trait: {details.analysis_summary?.dominant_personality_trait}
            </Typography>
            <Typography variant="caption" display="block">
              Communication Style: {details.analysis_summary?.communication_style}
            </Typography>
            <Typography variant="caption" display="block">
              Sentiment: {details.analysis_summary?.dominant_sentiment}
            </Typography>
          </Box>
        );
      
      case 'fine_tune_conversation':
        return (
          <Box>
            <Typography variant="body2" gutterBottom>
              <strong>Model Info:</strong>
            </Typography>
            <Typography variant="caption" display="block">
              Model ID: {details.model_id}
            </Typography>
            <Typography variant="caption" display="block">
              Type: {details.model_type}
            </Typography>
          </Box>
        );
      
      default:
        return null;
    }
  };

  const allStepsCompleted = processingSteps.every(step => stepStatus[step.id] === 'completed');
  const hasErrors = Object.values(stepStatus).some(status => status === 'error');

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h4" component="h2" gutterBottom align="center">
        Processing Pipeline
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph align="center">
        Session ID: {sessionId}
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {allStepsCompleted && (
        <Alert severity="success" sx={{ mb: 3 }}>
          All processing steps completed! Your digital avatar is ready for interaction.
        </Alert>
      )}

      <Box display="flex" gap={2} mb={3} justifyContent="center">
        <Button
          variant="contained"
          onClick={processAllSteps}
          disabled={processing || allStepsCompleted}
          startIcon={<PlayArrow />}
        >
          {processing ? 'Processing...' : 'Start All Steps'}
        </Button>
        
        <Button
          variant="outlined"
          onClick={checkSessionStatus}
          startIcon={<Refresh />}
        >
          Refresh Status
        </Button>
      </Box>

      <Stepper activeStep={activeStep} orientation="vertical">
        {processingSteps.map((step, index) => {
          const status = stepStatus[step.id];
          const details = stepDetails[step.id];
          const isExpanded = expandedSteps[step.id];

          return (
            <Step key={step.id} completed={status === 'completed'}>
              <StepLabel
                StepIconComponent={() => getStepIcon(step, status)}
                error={status === 'error'}
              >
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="h6">{step.label}</Typography>
                  <Chip
                    label={status || 'pending'}
                    color={getStepColor(status)}
                    size="small"
                    variant="outlined"
                  />
                  {details && (
                    <IconButton
                      size="small"
                      onClick={() => toggleStepExpansion(step.id)}
                    >
                      {isExpanded ? <ExpandLess /> : <ExpandMore />}
                    </IconButton>
                  )}
                </Box>
              </StepLabel>
              
              <StepContent>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {step.description}
                </Typography>
                
                {status === 'processing' && (
                  <Box sx={{ mb: 2 }}>
                    <LinearProgress />
                    <Typography variant="caption" color="text.secondary">
                      Processing...
                    </Typography>
                  </Box>
                )}
                
                <Collapse in={isExpanded}>
                  {details && (
                    <Card variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        {renderStepDetails(step, details)}
                      </CardContent>
                    </Card>
                  )}
                </Collapse>
                
                <Box display="flex" gap={1} mb={2}>
                  <Button
                    variant="contained"
                    size="small"
                    onClick={() => processStep(step)}
                    disabled={processing || status === 'completed'}
                  >
                    {status === 'completed' ? 'Completed' : 'Process Step'}
                  </Button>
                </Box>
              </StepContent>
            </Step>
          );
        })}
      </Stepper>

      {sessionStatus && (
        <Box mt={4}>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            Session Status
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Ready for interaction: {sessionStatus.ready_for_interaction ? 'Yes' : 'No'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total interactions: {sessionStatus.interaction_history?.total_interactions || 0}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default ProcessingStatus;