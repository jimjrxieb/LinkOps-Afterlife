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
  Divider
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
  Refresh
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
  
  const videoRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [conversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
            bgcolor: isUser ? 'primary.main' : isError ? 'error.main' : 'grey.100',
            color: isUser || isError ? 'white' : 'text.primary'
          }}
        >
          <CardContent sx={{ py: 1.5, px: 2, '&:last-child': { pb: 1.5 } }}>
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
        <Typography variant="h5" component="h2">
          Chat with Avatar
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Session: {sessionId}
        </Typography>
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
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={loading || !message.trim()}
            sx={{ minWidth: 60 }}
          >
            {loading ? <CircularProgress size={20} /> : <Send />}
          </Button>
        </Box>
        
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Press Enter to send, Shift+Enter for new line
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