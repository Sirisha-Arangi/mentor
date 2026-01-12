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
  Card,
  CardContent,
  CardActions,
  IconButton,
  Collapse
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import { 
  Upload as UploadIcon,
  ContentCopy as ContentCopyIcon,
  ExpandMore as ExpandMoreIcon,
  FlipToFront as FlipIcon
} from '@mui/icons-material';
import api from '../services/api';

interface Flashcard {
  id: number;
  question: string;
  answer: string;
  type: string;
  difficulty: string;
  topic: string;
}

interface FlashcardResponse {
  success: boolean;
  flashcards: Flashcard[];
  topic: string;
  total_cards: number;
  difficulty_level: string;
  card_types_used: string[];
  source_chunks_used: number;
}

const FlashcardsPage = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [flashcards, setFlashcards] = useState<Flashcard[]>([]);
  const [error, setError] = useState('');
  const [docId, setDocId] = useState('');
  const [topic, setTopic] = useState('');
  const [numCards, setNumCards] = useState(10);
  const [difficulty, setDifficulty] = useState('medium');
  const [cardTypes, setCardTypes] = useState<string[]>(['definition', 'concept']);
  const [flippedCards, setFlippedCards] = useState<Set<number>>(new Set());

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError('');
      setFlashcards([]);
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

  const handleGenerateFlashcards = async () => {
    if (!docId) {
      setError('Please upload a document first');
      return;
    }

    if (!topic.trim()) {
      setError('Please enter a topic for flashcard generation');
      return;
    }

    try {
      setIsUploading(true);
      const response = await api.post('/documents/generate-flashcards', {
        doc_id: docId,
        topic: topic.trim(),
        num_cards: numCards,
        difficulty: difficulty,
        card_types: cardTypes
      });
      
      if (response.data.success) {
        setFlashcards(response.data.flashcards);
        setError('');
      } else {
        setError(response.data.error || 'Failed to generate flashcards');
      }
    } catch (err) {
      setError('Failed to generate flashcards. Please try again.');
      console.error(err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleCopyContent = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleFlipCard = (cardId: number) => {
    setFlippedCards(prev => {
      const newSet = new Set(prev);
      if (newSet.has(cardId)) {
        newSet.delete(cardId);
      } else {
        newSet.add(cardId);
      }
      return newSet;
    });
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      default: return 'default';
    }
  };

  const getCardTypeColor = (type: string) => {
    switch (type) {
      case 'definition': return 'primary';
      case 'concept': return 'secondary';
      case 'application': return 'info';
      case 'example': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Flashcard Generator
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
            Flashcard Generation Settings
          </Typography>
          
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Topic for Flashcards"
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
                label="Number of Flashcards"
                value={numCards}
                onChange={(e) => setNumCards(parseInt(e.target.value) || 10)}
                inputProps={{ min: 1, max: 50 }}
                disabled={isUploading}
              />
            </Grid>
            
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  disabled={isUploading}
                >
                  <MenuItem value="easy">Easy</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="hard">Hard</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Card Types</InputLabel>
                <Select
                  multiple
                  value={cardTypes}
                  onChange={(e) => setCardTypes(e.target.value as string[])}
                  disabled={isUploading}
                >
                  <MenuItem value="definition">Definition</MenuItem>
                  <MenuItem value="concept">Concept</MenuItem>
                  <MenuItem value="application">Application</MenuItem>
                  <MenuItem value="example">Example</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Button
            variant="contained"
            onClick={handleGenerateFlashcards}
            disabled={!topic.trim() || isUploading}
            fullWidth
            size="large"
          >
            {isUploading ? (
              <>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                Generating Flashcards...
              </>
            ) : 'Generate Flashcards'}
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

      {flashcards.length > 0 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Generated Flashcards ({flashcards.length} cards)
          </Typography>
          
          <Grid container spacing={3}>
            {flashcards.map((flashcard) => (
              <Grid item xs={12} sm={6} md={4} key={flashcard.id}>
                <Card sx={{ height: '100%', minHeight: 200 }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                      <Typography variant="h6" component="div">
                        Card #{flashcard.id}
                      </Typography>
                      <Box>
                        <Chip 
                          label={flashcard.difficulty}
                          color={getDifficultyColor(flashcard.difficulty)}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                        <Chip 
                          label={flashcard.type}
                          color={getCardTypeColor(flashcard.type)}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Box sx={{ 
                      minHeight: 120, 
                      display: 'flex', 
                      alignItems: 'center',
                      justifyContent: 'center',
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      bgcolor: flippedCards.has(flashcard.id) ? 'grey.100' : 'background.paper'
                    }}>
                      <Typography 
                        variant="body1" 
                        align="center"
                        sx={{ 
                          fontWeight: flippedCards.has(flashcard.id) ? 'normal' : 'bold',
                          fontStyle: flippedCards.has(flashcard.id) ? 'italic' : 'normal'
                        }}
                      >
                        {flippedCards.has(flashcard.id) ? flashcard.answer : flashcard.question}
                      </Typography>
                    </Box>
                  </CardContent>
                  
                  <CardActions sx={{ justifyContent: 'space-between' }}>
                    <IconButton
                      onClick={() => handleFlipCard(flashcard.id)}
                      color="primary"
                      title="Flip card"
                    >
                      <FlipIcon />
                    </IconButton>
                    <Button
                      size="small"
                      startIcon={<ContentCopyIcon />}
                      onClick={() => handleCopyContent(
                        flippedCards.has(flashcard.id) 
                          ? flashcard.answer 
                          : flashcard.question
                      )}
                    >
                      Copy {flippedCards.has(flashcard.id) ? 'Answer' : 'Question'}
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

export default FlashcardsPage;