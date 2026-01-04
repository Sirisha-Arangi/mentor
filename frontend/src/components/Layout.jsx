import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material'
import { Link } from 'react-router-dom'

const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            AI Teaching Assistant
          </Typography>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>Home</Link>
            <Link to="/upload" style={{ color: 'white', textDecoration: 'none' }}>Upload</Link>
            <Link to="/search" style={{ color: 'white', textDecoration: 'none' }}>Search</Link>
          </Box>
        </Toolbar>
      </AppBar>
      <Container component="main" sx={{ mt: 4, mb: 4, flex: 1 }}>
        {children}
      </Container>
      <Box component="footer" sx={{ py: 3, px: 2, mt: 'auto', backgroundColor: '#f5f5f5' }}>
        <Container maxWidth="sm">
          <Typography variant="body2" color="text.secondary" align="center">
            © {new Date().getFullYear()} AI Teaching Assistant
          </Typography>
        </Container>
      </Box>
    </Box>
  )
}

export default Layout
