import { useState, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon } from '@mui/icons-material';
import api from '../services/api';
import SummaryResult from '../components/SummaryResult';

const SummarizerPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [summary, setSummary] = useState('');
  const [error, setError] = useState('');
  const [docId, setDocId] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsUploading(true);
      const response = await api.post('/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setDocId(response.data.id);
      setError('');
    } catch (err) {
      setError('Failed to upload document. Please try again.');
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!docId) {
      setError('Please upload a document first');
      return;
    }

    try {
      setIsUploading(true);
      const response = await api.post('/documents/summarize', {
        doc_id: docId,
        style: 'concise',
        length: 'medium'
      });
      setSummary(response.data.summary);
      setError('');
    } catch (err) {
      setError('Failed to generate summary. Please try again.');
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Document Summarizer
      </Typography>

      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: 'primary.main',
          textAlign: 'center',
          cursor: 'pointer',
          mb: 3,
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          '&:hover': {
            bgcolor: 'action.hover'
          }
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 48, mb: 2 }} />
        <Typography>
          {isDragActive
            ? 'Drop the file here...'
            : 'Drag and drop a document here, or click to select a file'}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Supported formats: PDF, DOCX, TXT
        </Typography>
      </Paper>

      {file && (
        <Box sx={{ mb: 3 }}>
          <Typography>Selected file: {file.name}</Typography>
          <Typography variant="body2" color="text.secondary">
            Size: {(file.size / 1024).toFixed(2)} KB
          </Typography>
        </Box>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </Button>

        <Button
          variant="outlined"
          onClick={handleGenerateSummary}
          disabled={!docId || isUploading}
        >
          {isUploading ? 'Generating...' : 'Generate Summary'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {summary && <SummaryResult content={summary} />}

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
        message={error}
      />
    </Box>
  );
};

export default SummarizerPage;
