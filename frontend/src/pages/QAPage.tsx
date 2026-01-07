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
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { Upload as UploadIcon } from '@mui/icons-material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import api from '../services/api';

interface QAPair {
  question: string;
  answer: string;
  type: string;
  difficulty: string;
  topic: string;
}

interface QAResponse {
  success: boolean;
  qa_pairs: QAPair[];
  topic: string;
  total_questions: number;
  difficulty_distribution: {
    easy: number;
    medium: number;
    hard: number;
  };
  topics_covered: string[];
  source_chunks_used: number;
}

const QAPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [qaPairs, setQAPairs] = useState<QAPair[]>([]);
  const [error, setError] = useState('');
  const [docId, setDocId] = useState('');
  const [topic, setTopic] = useState('');
  const [numQuestions, setNumQuestions] = useState(5);
  const [questionTypes, setQuestionTypes] = useState<string[]>(['conceptual', 'descriptive']);
  const [difficultyLevels, setDifficultyLevels] = useState<string[]>(['easy', 'medium']);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
      setQAPairs([]); // Clear previous Q&A pairs
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

  const handleGenerateQA = async () => {
    if (!docId) {
      setError('Please upload a document first');
      return;
    }

    if (!topic.trim()) {
      setError('Please enter a topic for Q&A generation');
      return;
    }

    try {
      setIsUploading(true);
      const response = await api.post('/documents/generate-qa', {
        doc_id: docId,
        topic: topic.trim(),
        num_questions: numQuestions,
        question_types: questionTypes,
        difficulty_levels: difficultyLevels
      });
      
      if (response.data.success) {
        setQAPairs(response.data.qa_pairs);
        setError('');
      } else {
        setError(response.data.error || 'Failed to generate Q&A pairs');
      }
    } catch (err) {
      setError('Failed to generate Q&A pairs. Please try again.');
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCopyAnswer = async (answer: string) => {
    try {
      await navigator.clipboard.writeText(answer);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const getQuestionTypeColor = (type: string) => {
    switch (type) {
      case 'conceptual': return 'primary';
      case 'descriptive': return 'secondary';
      case 'application': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Question & Answer Generator
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
            Q&A Generation Settings
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Topic for Q&A"
                placeholder="e.g., neural networks, machine learning, algorithms..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={isUploading}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                type="number"
                label="Number of Questions"
                value={numQuestions}
                onChange={(e) => setNumQuestions(parseInt(e.target.value) || 5)}
                inputProps={{ min: 1, max: 20 }}
                disabled={isUploading}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Question Types</InputLabel>
                <Select
                  multiple
                  value={questionTypes}
                  onChange={(e) => setQuestionTypes(e.target.value as string[])}
                  disabled={isUploading}
                >
                  <MenuItem value="conceptual">Conceptual</MenuItem>
                  <MenuItem value="descriptive">Descriptive</MenuItem>
                  <MenuItem value="application">Application</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Levels</InputLabel>
                <Select
                  multiple
                  value={difficultyLevels}
                  onChange={(e) => setDifficultyLevels(e.target.value as string[])}
                  disabled={isUploading}
                >
                  <MenuItem value="easy">Easy</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="hard">Hard</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Button
            variant="contained"
            onClick={handleGenerateQA}
            disabled={!topic.trim() || isUploading}
            fullWidth
            size="large"
          >
            {isUploading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Generating Q&A Pairs...
              </>
            ) : 'Generate Q&A Pairs'}
          </Button>
        </Paper>
      )}

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Button
          variant="outlined"
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

      {qaPairs.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Generated Q&A Pairs ({qaPairs.length} questions)
          </Typography>
          
          <Grid container spacing={2}>
            {qaPairs.map((qaPair, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="h6" component="div">
                        Question {index + 1}
                      </Typography>
                      <Box>
                        <Chip 
                          label={qaPair.difficulty}
                          color={getDifficultyColor(qaPair.difficulty)}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                        <Chip 
                          label={qaPair.type}
                          color={getQuestionTypeColor(qaPair.type)}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Typography variant="body1" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {qaPair.question}
                    </Typography>
                    
                    <Accordion>
                      <AccordionSummary 
                        expandIcon={<ExpandMoreIcon />}
                        sx={{ 
                          '& .MuiAccordionSummary-content': {
                            margin: 0
                          }
                        }}
                      >
                        <Typography variant="body2">Click to view answer</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            whiteSpace: 'pre-wrap',
                            lineHeight: 1.6 
                          }}
                        >
                          {qaPair.answer}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      startIcon={<ContentCopyIcon />}
                      onClick={() => handleCopyAnswer(qaPair.answer)}
                    >
                      Copy Answer
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError('')}
        message={error}
      />
    </Box>
  );
};

export default QAPage;