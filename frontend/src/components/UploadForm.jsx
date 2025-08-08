import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Divider,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Chip,
  Stack
} from '@mui/material';
import {
  CloudUpload,
  Photo,
  AudioFile,
  Description,
  Clear,
  Info
} from '@mui/icons-material';
import axios from 'axios';

const UploadForm = ({ onUploadSuccess, onSessionStart }) => {
  const [files, setFiles] = useState({
    photos: [],
    audio: null,
    text: null
  });
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [processingMethod, setProcessingMethod] = useState('best_selection');

  const handleFileChange = (fileType, event) => {
    if (fileType === 'photos') {
      const selectedFiles = Array.from(event.target.files);
      if (selectedFiles.length > 0) {
        // Limit to 10 photos max
        const limitedFiles = selectedFiles.slice(0, 10);
        setFiles(prev => ({
          ...prev,
          photos: limitedFiles
        }));
        setError(null);
        
        if (selectedFiles.length > 10) {
          setError('Maximum 10 photos allowed. Only the first 10 were selected.');
        }
      }
    } else {
      const file = event.target.files[0];
      if (file) {
        setFiles(prev => ({
          ...prev,
          [fileType]: file
        }));
        setError(null);
      }
    }
  };

  const removeFile = (fileType) => {
    if (fileType === 'photos') {
      setFiles(prev => ({
        ...prev,
        photos: []
      }));
    } else {
      setFiles(prev => ({
        ...prev,
        [fileType]: null
      }));
    }
  };

  const removePhoto = (index) => {
    setFiles(prev => ({
      ...prev,
      photos: prev.photos.filter((_, i) => i !== index)
    }));
  };

  const validateFiles = () => {
    const errors = [];
    
    if (!files.photos || files.photos.length === 0) {
      errors.push('At least one photo is required');
    } else {
      // Validate each photo
      for (let i = 0; i < files.photos.length; i++) {
        const photo = files.photos[i];
        if (!photo.type.startsWith('image/')) {
          errors.push(`Photo ${i + 1} must be an image file`);
        }
      }
    }
    
    if (!files.audio) {
      errors.push('Audio file is required');
    } else if (!files.audio.type.startsWith('audio/')) {
      errors.push('Audio must be an audio file');
    }
    
    if (!files.text) {
      errors.push('Text file is required');
    } else if (!files.text.type.startsWith('text/')) {
      errors.push('Text must be a text file');
    }
    
    return errors;
  };

  const handleUpload = async () => {
    const validationErrors = validateFiles();
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '));
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      
      // Append multiple photos
      files.photos.forEach((photo, index) => {
        formData.append('photos', photo);
      });
      
      formData.append('audio', files.audio);
      formData.append('text', files.text);

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(progress);
        },
      });

      setSuccess('Files uploaded successfully! Starting session...');
      
      // Call success handlers
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
      
      if (onSessionStart) {
        onSessionStart(response.data.session_id);
      }

      // Reset form after successful upload
      setTimeout(() => {
        setFiles({ photos: [], audio: null, text: null });
        setSuccess(null);
      }, 3000);

    } catch (err) {
      console.error('Upload error:', err);
      setError(
        err.response?.data?.detail || 
        'Upload failed. Please check your files and try again.'
      );
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const FileUploadCard = ({ 
    title, 
    fileType, 
    icon: Icon, 
    accept, 
    description, 
    file 
  }) => (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Icon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6" component="h3">
            {title}
          </Typography>
          <Tooltip title={description} placement="top">
            <IconButton size="small" sx={{ ml: 'auto' }}>
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Typography variant="body2" color="text.secondary" mb={2}>
          {description}
        </Typography>
        
        {file ? (
          <Box>
            <Alert severity="success" sx={{ mb: 2 }}>
              Selected: {file.name}
              <br />
              Size: {(file.size / 1024 / 1024).toFixed(2)} MB
            </Alert>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => document.getElementById(`${fileType}-input`).click()}
              >
                Change File
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="error"
                startIcon={<Clear />}
                onClick={() => removeFile(fileType)}
              >
                Remove
              </Button>
            </Box>
          </Box>
        ) : (
          <Button
            variant="outlined"
            fullWidth
            onClick={() => document.getElementById(`${fileType}-input`).click()}
            sx={{ minHeight: 60, borderStyle: 'dashed' }}
          >
            <CloudUpload sx={{ mr: 1 }} />
            Choose {title}
          </Button>
        )}
        
        <input
          id={`${fileType}-input`}
          type="file"
          accept={accept}
          style={{ display: 'none' }}
          onChange={(e) => handleFileChange(fileType, e)}
        />
      </CardContent>
    </Card>
  );

  const PhotoUploadCard = () => (
    <Card variant="outlined" sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Photo color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6" component="h3">
            Photos ({files.photos.length}/10)
          </Typography>
          <Tooltip title="Upload multiple clear photos of the person for enhanced avatar quality using AI processing" placement="top">
            <IconButton size="small" sx={{ ml: 'auto' }}>
              <Info fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        
        <Typography variant="body2" color="text.secondary" mb={2}>
          Upload 1-10 clear photos. AI will automatically select the best photo or create an averaged face for higher quality avatars.
        </Typography>
        
        {files.photos.length > 0 ? (
          <Box>
            <Stack direction="row" spacing={1} flexWrap="wrap" mb={2}>
              {files.photos.map((photo, index) => (
                <Chip
                  key={index}
                  label={`${photo.name.substring(0, 20)}...`}
                  onDelete={() => removePhoto(index)}
                  size="small"
                  sx={{ mb: 1 }}
                />
              ))}
            </Stack>
            <Alert severity="success" sx={{ mb: 2 }}>
              {files.photos.length} photo{files.photos.length > 1 ? 's' : ''} selected
              <br />
              Total size: {(files.photos.reduce((sum, photo) => sum + photo.size, 0) / 1024 / 1024).toFixed(2)} MB
            </Alert>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                size="small"
                onClick={() => document.getElementById('photos-input').click()}
              >
                Add More Photos
              </Button>
              <Button
                variant="outlined"
                size="small"
                color="error"
                startIcon={<Clear />}
                onClick={() => removeFile('photos')}
              >
                Remove All
              </Button>
            </Box>
          </Box>
        ) : (
          <Button
            variant="outlined"
            fullWidth
            onClick={() => document.getElementById('photos-input').click()}
            sx={{ minHeight: 60, borderStyle: 'dashed' }}
          >
            <CloudUpload sx={{ mr: 1 }} />
            Choose Photos (1-10)
          </Button>
        )}
        
        <input
          id="photos-input"
          type="file"
          accept="image/*"
          multiple
          style={{ display: 'none' }}
          onChange={(e) => handleFileChange('photos', e)}
        />
      </CardContent>
    </Card>
  );

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 1000, mx: 'auto' }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Create Your Digital Afterlife
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph align="center">
        Upload your files to begin creating an AI-powered avatar that reflects your personality
      </Typography>
      
      <Divider sx={{ my: 3 }} />

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <PhotoUploadCard />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <FileUploadCard
            title="Audio"
            fileType="audio"
            icon={AudioFile}
            accept="audio/*"
            description="Audio recording of the person's voice for voice cloning. At least 30 seconds recommended."
            file={files.audio}
          />
        </Grid>
        
        <Grid item xs={12} md={4}>
          <FileUploadCard
            title="Text"
            fileType="text"
            icon={Description}
            accept="text/*"
            description="Text samples of the person's writing style, messages, or conversations for personality analysis."
            file={files.text}
          />
        </Grid>
      </Grid>

      {/* AI Processing Method Selection */}
      {files.photos.length > 1 && (
        <Box sx={{ mb: 4 }}>
          <FormControl component="fieldset">
            <FormLabel component="legend">
              <Typography variant="h6" gutterBottom>
                AI Photo Processing Method
              </Typography>
            </FormLabel>
            <RadioGroup
              value={processingMethod}
              onChange={(e) => setProcessingMethod(e.target.value)}
              row
            >
              <FormControlLabel
                value="best_selection"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body2" fontWeight="bold">
                      Best Selection
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      AI analyzes all photos and selects the highest quality one based on face detection, sharpness, and lighting
                    </Typography>
                  </Box>
                }
              />
              <FormControlLabel
                value="face_averaging"
                control={<Radio />}
                label={
                  <Box>
                    <Typography variant="body2" fontWeight="bold">
                      Face Averaging
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      AI creates a composite face by averaging features from all photos for enhanced consistency
                    </Typography>
                  </Box>
                }
              />
            </RadioGroup>
          </FormControl>
        </Box>
      )}

      {uploading && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" gutterBottom>
            Uploading files... {uploadProgress}%
          </Typography>
          <LinearProgress variant="determinate" value={uploadProgress} />
        </Box>
      )}

      <Box display="flex" justifyContent="center">
        <Button
          variant="contained"
          size="large"
          onClick={handleUpload}
          disabled={uploading || files.photos.length === 0 || !files.audio || !files.text}
          sx={{ minWidth: 200, py: 1.5 }}
        >
          {uploading ? 'Uploading...' : 'Start Processing'}
        </Button>
      </Box>

      <Box mt={3}>
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Privacy Note:</strong> Your files will be processed to create a digital avatar.
            Please ensure you have appropriate consent for using this person's likeness, voice, and text data.
          </Typography>
        </Alert>
      </Box>
    </Paper>
  );
};

export default UploadForm;