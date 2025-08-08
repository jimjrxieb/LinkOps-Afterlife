import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  Grid,
  TextField,
  InputAdornment,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  History,
  PlayArrow,
  Download,
  Search,
  FilterList,
  Refresh,
  Videocam,
  Schedule,
  Person,
  SmartToy,
  ExpandMore,
  Clear
} from '@mui/icons-material';
import axios from 'axios';

const SessionHistory = ({ sessionId }) => {
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoDialog, setVideoDialog] = useState(false);
  const [expandedInteraction, setExpandedInteraction] = useState(null);

  useEffect(() => {
    if (sessionId) {
      fetchInteractionHistory();
    }
  }, [sessionId]);

  const fetchInteractionHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/interaction_history/${sessionId}`);
      const historyData = response.data.interaction_history;
      
      if (historyData && historyData.interactions) {
        setInteractions(historyData.interactions.reverse()); // Most recent first
      } else {
        setInteractions([]);
      }
    } catch (err) {
      console.error('Error fetching interaction history:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to load interaction history'
      );
    } finally {
      setLoading(false);
    }
  };

  const filteredInteractions = interactions.filter(interaction =>
    interaction.user_input.toLowerCase().includes(searchTerm.toLowerCase()) ||
    interaction.generated_response.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const playVideo = (videoPath) => {
    setSelectedVideo(videoPath);
    setVideoDialog(true);
  };

  const downloadVideo = (videoPath, timestamp) => {
    const link = document.createElement('a');
    link.href = `/api/download/${videoPath}`;
    link.download = `avatar_${timestamp.replace(/[:.]/g, '-')}.mp4`;
    link.click();
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const formatDuration = (timestamp) => {
    const now = new Date();
    const interactionTime = new Date(timestamp);
    const diffMs = now - interactionTime;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  const getFileSizeString = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderInteractionCard = (interaction, index) => {
    const isExpanded = expandedInteraction === interaction.interaction_timestamp;

    return (
      <Accordion
        key={interaction.interaction_timestamp}
        expanded={isExpanded}
        onChange={() => setExpandedInteraction(
          isExpanded ? null : interaction.interaction_timestamp
        )}
      >
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box display="flex" alignItems="center" width="100%" mr={2}>
            <Box flex={1}>
              <Typography variant="subtitle1" noWrap>
                {interaction.user_input}
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                <Chip
                  icon={<Schedule />}
                  label={formatDuration(interaction.interaction_timestamp)}
                  size="small"
                  variant="outlined"
                />
                <Chip
                  icon={<Videocam />}
                  label={getFileSizeString(interaction.video_file_size)}
                  size="small"
                  variant="outlined"
                />
              </Box>
            </Box>
          </Box>
        </AccordionSummary>
        
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <Person sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="subtitle2">User Input</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {interaction.user_input}
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    {formatTimestamp(interaction.interaction_timestamp)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Box display="flex" alignItems="center" mb={1}>
                    <SmartToy sx={{ mr: 1, color: 'secondary.main' }} />
                    <Typography variant="subtitle2">Avatar Response</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    {interaction.generated_response}
                  </Typography>
                  <Box display="flex" gap={1} mt={2}>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<PlayArrow />}
                      onClick={() => playVideo(interaction.video_path)}
                    >
                      Play Video
                    </Button>
                    <Button
                      size="small"
                      variant="outlined"
                      startIcon={<Download />}
                      onClick={() => downloadVideo(
                        interaction.video_path, 
                        interaction.interaction_timestamp
                      )}
                    >
                      Download
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12}>
              <Divider sx={{ my: 1 }} />
              <Typography variant="caption" color="text.secondary">
                Processing Steps: {interaction.processing_steps?.join(' → ')}
              </Typography>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>
    );
  };

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box display="flex" alignItems="center">
          <History sx={{ mr: 1 }} />
          <Typography variant="h5" component="h2">
            Interaction History
          </Typography>
        </Box>
        
        <Box display="flex" gap={1}>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchInteractionHistory} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Search and Filter */}
      <Box mb={3}>
        <TextField
          fullWidth
          placeholder="Search interactions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton onClick={() => setSearchTerm('')} size="small">
                  <Clear />
                </IconButton>
              </InputAdornment>
            )
          }}
          size="small"
        />
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <Typography>Loading interaction history...</Typography>
        </Box>
      ) : filteredInteractions.length === 0 ? (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          py={6}
        >
          <History sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            {searchTerm ? 'No interactions found' : 'No interactions yet'}
          </Typography>
          <Typography variant="body2" color="text.secondary" align="center">
            {searchTerm 
              ? 'Try adjusting your search terms'
              : 'Start chatting with your avatar to see interaction history here'
            }
          </Typography>
        </Box>
      ) : (
        <Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {filteredInteractions.length} interaction{filteredInteractions.length !== 1 ? 's' : ''}
            {searchTerm && ` matching "${searchTerm}"`}
          </Typography>
          
          <Box mt={2}>
            {filteredInteractions.map(renderInteractionCard)}
          </Box>
        </Box>
      )}

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
          {selectedVideo && (
            <video
              src={`/api/video/${selectedVideo}`}
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
          <Button 
            onClick={() => downloadVideo(selectedVideo, 'download')}
            startIcon={<Download />}
          >
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

export default SessionHistory;