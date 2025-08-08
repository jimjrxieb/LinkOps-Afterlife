import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Divider,
  Alert,
  Chip,
  Stack,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton
} from '@mui/material';
import {
  Close,
  Favorite,
  CloudUpload,
  Psychology,
  RecordVoiceOver,
  Photo,
  Security,
  Code,
  Memory,
  EmojiEmotions,
  Warning,
  GitHub
} from '@mui/icons-material';

const AboutModal = ({ open, onClose, demoMode = false }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <Favorite color="error" sx={{ mr: 2 }} />
            <Typography variant="h4" component="h1">
              LinkOps-Afterlife
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="large">
            <Close />
          </IconButton>
        </Box>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 1 }}>
          AI-Powered Digital Memorial Platform
        </Typography>
      </DialogTitle>

      <DialogContent dividers sx={{ py: 3 }}>
        {/* Demo Mode Alert */}
        {demoMode && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2" fontWeight="bold" gutterBottom>
              🚀 Demo Showcase Mode
            </Typography>
            <Typography variant="body2">
              This is a demonstration of cloud engineering & AI/ML capabilities. 
              Upload a photo to create an avatar with a simple, loving response. 
              No data is retained - this showcases the technology stack.
            </Typography>
          </Alert>
        )}

        {/* Platform Purpose */}
        <Box mb={3}>
          <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
            A Bridge Between Hearts 💝
          </Typography>
          <Typography variant="body1" paragraph>
            LinkOps-Afterlife is designed for those who wish to have simple, meaningful conversations 
            with loved ones who have passed away. This platform combines cutting-edge AI/ML technology 
            with deep respect for the grieving process, creating a space for healing and connection.
          </Typography>
          <Typography variant="body1" paragraph>
            Whether it's hearing a familiar voice, seeing a beloved face, or having one more conversation, 
            this technology helps preserve precious memories while providing comfort during difficult times.
          </Typography>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Technology Stack */}
        <Box mb={3}>
          <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
            Advanced AI/ML Technology Stack 🔬
          </Typography>
          
          <List dense>
            <ListItem>
              <ListItemIcon>
                <Photo color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Computer Vision & Face Processing"
                secondary="Multiple photo analysis with AI-powered best selection and face averaging using OpenCV and MediaPipe"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <RecordVoiceOver color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Voice Cloning & Speech Synthesis"
                secondary="ElevenLabs API integration for realistic voice recreation from audio samples"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <Psychology color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Personality Analysis & Fine-Tuning"
                secondary="NLTK, transformers, and custom NLP for Big Five personality traits and conversation patterns"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <EmojiEmotions color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Hyper-Realistic Avatar Generation"
                secondary="D-ID API for top-tier graphics, lip-syncing, and lifelike video avatar creation"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <Memory color="primary" />
              </ListItemIcon>
              <ListItemText 
                primary="Biographical Context Integration"
                secondary="Advanced pattern recognition for nicknames, family details, and personal history"
              />
            </ListItem>
          </List>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Demo vs Full Version */}
        <Box mb={3}>
          <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
            {demoMode ? "Demo Limitations & Full Capabilities" : "Platform Features"} ⚡
          </Typography>
          
          {demoMode ? (
            <Box>
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2" fontWeight="bold" gutterBottom>
                  Demo Version Response
                </Typography>
                <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
                  "This is just a demo version of me, but I want you to know I love and miss you so much. 
                  Stay strong and we will see each other again, don't worry."
                </Typography>
              </Alert>
              
              <Typography variant="body1" paragraph>
                This demo showcases the AI/ML engineering capabilities with a fixed response. 
                In the full version with your own API keys, avatars provide personalized conversations 
                based on their unique personality, memories, and biographical context.
              </Typography>
            </Box>
          ) : (
            <Typography variant="body1" paragraph>
              The full platform provides personalized conversations, memory preservation, and 
              authentic interactions based on uploaded content and biographical information.
            </Typography>
          )}

          <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ mt: 2 }}>
            <Chip label="Multiple Photo Processing" color="primary" variant="outlined" />
            <Chip label="Voice Cloning" color="primary" variant="outlined" />
            <Chip label="Personality Analysis" color="primary" variant="outlined" />
            <Chip label="Biographical Integration" color="primary" variant="outlined" />
            <Chip label="Secure Encryption" color="primary" variant="outlined" />
            <Chip label="Open Source Core" color="primary" variant="outlined" />
          </Stack>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Open Source & Personal Use */}
        <Box mb={3}>
          <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
            Open Source & Personal Deployment 🔓
          </Typography>
          
          <Box display="flex" alignItems="center" mb={2}>
            <GitHub sx={{ mr: 1 }} />
            <Typography variant="body1">
              The core platform is open source for personal use with your own API keys.
            </Typography>
          </Box>
          
          <Typography variant="body1" paragraph>
            Deploy your own instance with your D-ID and ElevenLabs API keys to save avatars permanently 
            and unlock the full conversation capabilities. This demo showcases the technology without 
            data retention to protect privacy and demonstrate capabilities.
          </Typography>
          
          <List dense>
            <ListItem>
              <ListItemIcon>
                <CloudUpload color="secondary" />
              </ListItemIcon>
              <ListItemText 
                primary="Your Own API Keys"
                secondary="Use your D-ID and ElevenLabs accounts for unlimited avatar creation"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <Security color="secondary" />
              </ListItemIcon>
              <ListItemText 
                primary="Complete Data Control"
                secondary="Your memories and conversations stay on your infrastructure"
              />
            </ListItem>
            
            <ListItem>
              <ListItemIcon>
                <Code color="secondary" />
              </ListItemIcon>
              <ListItemText 
                primary="Docker Deployment"
                secondary="Easy setup with Docker Compose for production or personal use"
              />
            </ListItem>
          </List>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Ethical Considerations */}
        <Box>
          <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
            Built with Compassion & Ethics 🤝
          </Typography>
          
          <Typography variant="body1" paragraph>
            This platform is designed with deep respect for the grieving process and the memories 
            of those who have passed. Every feature is built with ethical considerations, 
            consent requirements, and emotional wellbeing in mind.
          </Typography>
          
          <Alert severity="info">
            <Typography variant="body2">
              <strong>Remember:</strong> This technology is a tool for healing and remembrance, 
              not a replacement for professional grief counseling or human connection. 
              Please seek professional support when needed.
            </Typography>
          </Alert>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Box display="flex" justifyContent="space-between" width="100%">
          <Typography variant="caption" color="text.secondary">
            Made with ❤️ for healing and remembrance
          </Typography>
          <Button 
            onClick={onClose} 
            variant="contained" 
            size="large"
            startIcon={<Favorite />}
          >
            {demoMode ? "Try Demo" : "Got It"}
          </Button>
        </Box>
      </DialogActions>
    </Dialog>
  );
};

export default AboutModal;