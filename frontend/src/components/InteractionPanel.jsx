import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  Send,
  Videocam,
  PlayArrow,
  Pause,
  VolumeUp,
  VolumeOff,
  Fullscreen,
  Download,
  Refresh,
  Person
} from '@mui/icons-material';
import axios from 'axios';

const InteractionPanel = ({ sessionId }) => {
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentVideo, setCurrentVideo] = useState(null);
  const [videoLoading, setVideoLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [videoDialog, setVideoDialog] = useState(false);
  
  // Persona state
  const [selectedPersona, setSelectedPersona] = useState('james');
  const [availablePersonas, setAvailablePersonas] = useState([]);
  const [personaInfo, setPersonaInfo] = useState(null);
  const [personaLoading, setPersonaLoading] = useState(false);
  
  const videoRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [conversations]);

  useEffect(() => {
    loadAvailablePersonas();
    if (selectedPersona) {
      loadPersonaInfo(selectedPersona);
    }
  }, []);

  useEffect(() => {
    if (selectedPersona) {
      loadPersonaInfo(selectedPersona);
    }
  }, [selectedPersona]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Persona management functions
  const loadAvailablePersonas = async () => {
    try {
      const response = await axios.get('/personas');
      setAvailablePersonas(response.data.personas || []);
    } catch (error) {
      console.error('Error loading personas:', error);
      setAvailablePersonas(['james']); // Fallback to default
    }
  };

  const loadPersonaInfo = async (personaId) => {
    setPersonaLoading(true);
    try {
      const response = await axios.get(`/personas/${personaId}`);
      setPersonaInfo(response.data.persona);
    } catch (error) {
      console.error('Error loading persona info:', error);
      setPersonaInfo(null);
    }
    setPersonaLoading(false);
  };

  const handlePersonaChange = (event) => {
    setSelectedPersona(event.target.value);
  };

  // Simple persona chat function (without video generation)
  const handlePersonaChat = async () => {
    if (!message.trim()) return;
    
    const userMessage = message.trim();
    setMessage('');
    setLoading(true);
    setError(null);
    
    // Add user message to conversation
    setConversations(prev => [
      ...prev,
      {
        id: Date.now(),
        type: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      }
    ]);

    try {
      const response = await axios.post('/chat', {
        message: userMessage,
        persona_id: selectedPersona,
        context: ""
      });

      const chatResponse = response.data.response;
      
      // Add persona response to conversation
      setConversations(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'persona',
          content: chatResponse.answer,
          persona_name: chatResponse.persona_name,
          matched_qa: chatResponse.matched_qa,
          tts_voice: chatResponse.tts_voice,
          timestamp: new Date().toISOString()
        }
      ]);

    } catch (err) {
      console.error('Persona chat error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to generate response. Please try again.'
      );
      
      // Add error message to conversation
      setConversations(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'error',
          content: 'Sorry, I encountered an error generating a response.',
          timestamp: new Date().toISOString()
        }
      ]);
    }
    
    setLoading(false);
  };

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage('');
    setLoading(true);
    setError(null);
    setVideoLoading(true);

    // Add user message to conversation
    setConversations(prev => [
      ...prev,
      {
        id: Date.now(),
        type: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      }
    ]);

    try {
      const response = await axios.post(`/api/interact/${sessionId}`, {
        input: userMessage
      });

      const avatarResponse = {
        id: Date.now() + 1,
        type: 'avatar',
        content: response.data.user_input,
        response: response.data,
        videoPath: response.data.video_path,
        timestamp: response.data.generation_timestamp
      };

      setConversations(prev => [...prev, avatarResponse]);
      setCurrentVideo(response.data.video_path);

    } catch (err) {
      console.error('Interaction error:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to generate response. Please try again.'
      );
      
      // Add error message to conversation
      setConversations(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'error',
          content: 'Sorry, I encountered an error generating a response.',
          timestamp: new Date().toISOString()
        }
      ]);
    } finally {
      setLoading(false);
      setVideoLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const downloadVideo = () => {
    if (currentVideo) {
      const link = document.createElement('a');
      link.href = `/api/download/${currentVideo}`;
      link.download = `avatar_response_${Date.now()}.mp4`;
      link.click();
    }
  };

  const openVideoDialog = () => {
    setVideoDialog(true);
  };

  const renderMessage = (conversation) => {
    const isUser = conversation.type === 'user';
    const isError = conversation.type === 'error';
    const isPersona = conversation.type === 'persona';

    return (
      <Box
        key={conversation.id}
        display="flex"
        justifyContent={isUser ? 'flex-end' : 'flex-start'}
        mb={2}
      >
        <Card
          sx={{
            maxWidth: '70%',
            bgcolor: isUser ? 'primary.main' : isError ? 'error.main' : isPersona ? 'secondary.light' : 'grey.100',
            color: isUser || isError ? 'white' : 'text.primary'
          }}
        >
          <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
            {/* Persona header */}
            {isPersona && conversation.persona_name && (
              <Box display="flex" alignItems="center" gap={1} mb={1}>
                <Person fontSize="small" />
                <Typography variant="caption" fontWeight="bold">
                  {conversation.persona_name}
                </Typography>
                {conversation.matched_qa && (
                  <Chip
                    label="Pinned Q&A"
                    size="small"
                    color="primary"
                    variant="outlined"
                    sx={{ height: 16, fontSize: '0.65rem' }}
                  />
                )}
              </Box>
            )}
            
            <Typography variant="body1">
              {conversation.content}
            </Typography>
            
            {conversation.videoPath && (
              <Box mt={1}>
                <Chip
                  icon={<Videocam />}
                  label="Video Response Available"
                  size="small"
                  onClick={() => {
                    setCurrentVideo(conversation.videoPath);
                    openVideoDialog();
                  }}
                  sx={{ cursor: 'pointer' }}
                />
              </Box>
            )}
            
            <Typography variant="caption" display="block" sx={{ mt: 0.5, opacity: 0.7 }}>
              {new Date(conversation.timestamp).toLocaleTimeString()}
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  };

  return (
    <Paper elevation={3} sx={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box p={2} borderBottom={1} borderColor="divider">
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h5" component="h2">
              Chat with Avatar
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Session: {sessionId}
            </Typography>
          </Box>
          
          {/* Persona Selector */}
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Persona</InputLabel>
            <Select
              value={selectedPersona}
              onChange={handlePersonaChange}
              label="Persona"
              startAdornment={<Person sx={{ mr: 1, color: 'action.active' }} />}
            >
              {availablePersonas.map((persona) => (
                <MenuItem key={persona} value={persona}>
                  {persona.charAt(0).toUpperCase() + persona.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
        
        {/* Persona Info */}
        {personaInfo && !personaLoading && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>{personaInfo.display_name}</strong> - {personaInfo.style.tone}
            </Typography>
            <Typography variant="caption" display="block">
              {personaInfo.memory.bio.substring(0, 100)}...
            </Typography>
          </Alert>
        )}
      </Box>

      {/* Current Video Display */}
      {currentVideo && (
        <Box p={2} borderBottom={1} borderColor="divider">
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Typography variant="h6">Current Response</Typography>
            <Box>
              <Tooltip title="Play/Pause">
                <IconButton onClick={togglePlayPause} disabled={videoLoading}>
                  {isPlaying ? <Pause /> : <PlayArrow />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Mute/Unmute">
                <IconButton onClick={toggleMute}>
                  {isMuted ? <VolumeOff /> : <VolumeUp />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Fullscreen">
                <IconButton onClick={openVideoDialog}>
                  <Fullscreen />
                </IconButton>
              </Tooltip>
              <Tooltip title="Download">
                <IconButton onClick={downloadVideo}>
                  <Download />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          {videoLoading ? (
            <Box display="flex" justifyContent="center" alignItems="center" height={200}>
              <CircularProgress />
              <Typography variant="body2" ml={2}>
                Generating avatar response...
              </Typography>
            </Box>
          ) : (
            <video
              ref={videoRef}
              src={`/api/video/${currentVideo}`}
              style={{
                width: '100%',
                maxHeight: '200px',
                borderRadius: '8px'
              }}
              controls
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
          )}
        </Box>
      )}

      {/* Messages Area */}
      <Box
        flex={1}
        p={2}
        sx={{
          overflowY: 'auto',
          bgcolor: 'grey.50'
        }}
      >
        {conversations.length === 0 ? (
          <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="100%"
            flexDirection="column"
          >
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Start a Conversation
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              Type a message below to begin interacting with your digital avatar.
              The avatar will respond with a personalized video message.
            </Typography>
          </Box>
        ) : (
          <>
            {conversations.map(renderMessage)}
            <div ref={messagesEndRef} />
          </>
        )}
      </Box>

      {/* Error Display */}
      {error && (
        <Box p={2}>
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Box>
      )}

      {/* Input Area */}
      <Box p={2} borderTop={1} borderColor="divider">
        <Box display="flex" gap={1}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder="Type your message here..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
            variant="outlined"
            size="small"
          />
          <Box display="flex" flexDirection="column" gap={1}>
            <Tooltip title="Quick persona chat (text only)">
              <Button
                variant="outlined"
                onClick={handlePersonaChat}
                disabled={loading || !message.trim()}
                sx={{ minWidth: 60, flex: 1 }}
                size="small"
              >
                {loading ? <CircularProgress size={16} /> : <Send />}
              </Button>
            </Tooltip>
            <Tooltip title="Full avatar response (video + voice)">
              <Button
                variant="contained"
                onClick={handleSendMessage}
                disabled={loading || !message.trim()}
                sx={{ minWidth: 60, flex: 1 }}
                size="small"
              >
                {loading ? <CircularProgress size={16} /> : <Videocam />}
              </Button>
            </Tooltip>
          </Box>
        </Box>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Text: Quick persona response | Video: Full avatar with voice
        </Typography>
      </Box>

      {/* Video Dialog */}
      <Dialog
        open={videoDialog}
        onClose={() => setVideoDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Avatar Response Video
          <IconButton
            onClick={() => setVideoDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            ×
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {currentVideo && (
            <video
              src={`/api/video/${currentVideo}`}
              style={{
                width: '100%',
                height: 'auto'
              }}
              controls
              autoPlay
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={downloadVideo} startIcon={<Download />}>
            Download
          </Button>
          <Button onClick={() => setVideoDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default InteractionPanel;