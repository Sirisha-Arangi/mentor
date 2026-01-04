import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Container, Box } from '@mui/material';
import DocumentUpload from './components/DocumentUpload';
import theme from './theme/theme';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                AI Teaching Assistant
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Home</Link>
                <Link to="/upload" style={{ color: 'white', textDecoration: 'none' }}>Upload</Link>
              </Box>
            </Toolbar>
          </AppBar>
          <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Routes>
              <Route path="/upload" element={<DocumentUpload />} />
              <Route path="/" element={
                <Box sx={{ textAlign: 'center', mt: 4 }}>
                  <Typography variant="h4" gutterBottom>
                    Welcome to AI Teaching Assistant
                  </Typography>
                  <Typography variant="body1" paragraph>
                    Upload your teaching materials to get started with document analysis and content generation.
                  </Typography>
                </Box>
              } />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;