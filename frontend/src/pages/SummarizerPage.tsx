import { useState, useCallback } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  CircularProgress,
  Alert,
  Snackbar,
  TextField,
  Grid
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
  const [topic, setTopic] = useState('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
      setSummary(''); // Clear previous summary
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

  const handleGenerateTopicSummary = async () => {
    if (!docId) {
      setError('Please upload a document first');
      return;
    }

    if (!topic.trim()) {
      setError('Please enter a topic to summarize');
      return;
    }

    try {
      setIsUploading(true);
      const response = await api.post('/documents/topic-summary', {
        doc_id: docId,
        topic: topic.trim(),
        style: 'concise',
        length: 'medium'
      });
      setSummary(response.data.summary);
      setError('');
    } catch (err) {
      setError('Failed to generate topic summary. Please try again.');
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

      {docId && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Topic-Specific Summary
          </Typography>
          <TextField
            fullWidth
            label="Enter topic to summarize"
            placeholder="e.g., neural networks, machine learning, data structures..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            sx={{ mb: 2 }}
            disabled={isUploading}
          />
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Enter a specific topic from your document to generate a focused summary
          </Typography>
          <Button
            variant="contained"
            onClick={handleGenerateTopicSummary}
            disabled={!topic.trim() || isUploading}
            fullWidth
          >
            {isUploading ? 'Generating Topic Summary...' : 'Generate Topic Summary'}
          </Button>
        </Paper>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="outlined"
          onClick={handleGenerateSummary}
          disabled={!docId || isUploading}
        >
          {isUploading ? 'Generating...' : 'Generate Full Summary'}
        </Button>

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || isUploading}
        >
          {isUploading ? 'Uploading...' : 'Upload Document'}
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