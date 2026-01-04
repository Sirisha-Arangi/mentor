import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  LinearProgress,
  IconButton
} from '@mui/material';
import { 
  CloudUpload as CloudUploadIcon, 
  InsertDriveFile as FileIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { documentService } from '../services/documentService';

const DocumentUpload = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      progress: 0,
      status: 'pending'
    }));
    setFiles(prevFiles => [...prevFiles, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxSize: 10 * 1024 * 1024, // 10MB
    multiple: true
  });

  const removeFile = (fileId) => {
    setFiles(files.filter(file => file.id !== fileId));
  };

  const uploadFiles = async () => {
    setUploading(true);
    
    for (const fileObj of files) {
      if (fileObj.status === 'pending') {
        try {
          setFiles(prevFiles => 
            prevFiles.map(f => 
              f.id === fileObj.id ? { ...f, status: 'uploading' } : f
            )
          );

          await documentService.uploadDocument(
            fileObj.file,
            (progress) => {
              setUploadProgress(prev => ({
                ...prev,
                [fileObj.id]: progress
              }));
            }
          );

          setFiles(prevFiles => 
            prevFiles.map(f => 
              f.id === fileObj.id ? { ...f, status: 'completed' } : f
            )
          );
        } catch (error) {
          console.error('Upload error:', error);
          setFiles(prevFiles => 
            prevFiles.map(f => 
              f.id === fileObj.id ? { ...f, status: 'error' } : f
            )
          );
        }
      }
    }
    
    setUploading(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'error': return 'error';
      case 'uploading': return 'primary';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ maxWidth: 800, margin: '0 auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Upload Teaching Materials
      </Typography>
      
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.400',
          backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
          textAlign: 'center',
          cursor: 'pointer',
          mb: 3
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography>
          {isDragActive
            ? 'Drop the files here...'
            : 'Drag and drop files here, or click to select files'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Supported formats: PDF, DOCX, TXT (Max 10MB)
        </Typography>
      </Paper>

      {files.length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Selected Files ({files.length})
          </Typography>
          <List>
            {files.map((fileObj) => (
              <ListItem
                key={fileObj.id}
                secondaryAction={
                  fileObj.status !== 'uploading' && (
                    <IconButton 
                      edge="end" 
                      onClick={() => removeFile(fileObj.id)}
                      disabled={uploading}
                    >
                      <CloseIcon />
                    </IconButton>
                  )
                }
              >
                <ListItemIcon>
                  <FileIcon color={getStatusColor(fileObj.status)} />
                </ListItemIcon>
                <Box sx={{ flexGrow: 1, mr: 2 }}>
                  <ListItemText 
                    primary={fileObj.file.name} 
                    secondary={`${(fileObj.file.size / 1024 / 1024).toFixed(2)} MB`} 
                  />
                  {fileObj.status === 'uploading' && (
                    <LinearProgress 
                      variant="determinate" 
                      value={uploadProgress[fileObj.id] || 0} 
                      sx={{ mt: 1 }} 
                    />
                  )}
                  {fileObj.status === 'completed' && (
                    <Typography variant="caption" color="success.main">
                      Uploaded successfully
                    </Typography>
                  )}
                  {fileObj.status === 'error' && (
                    <Typography variant="caption" color="error">
                      Upload failed
                    </Typography>
                  )}
                </Box>
              </ListItem>
            ))}
          </List>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={uploadFiles}
              disabled={uploading || files.every(f => f.status === 'completed')}
            >
              {uploading ? 'Uploading...' : 'Upload Files'}
            </Button>
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default DocumentUpload;