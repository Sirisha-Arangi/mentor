import { Drawer, List, ListItem, ListItemIcon, ListItemText, Toolbar, Box, styled } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Summarize as SummarizeIcon,
  Quiz as QuizIcon,
  FlashOn as FlashOnIcon,
  Schedule as ScheduleIcon,
  CompareArrows as CompareArrowsIcon,
  Assignment as AssignmentIcon,
  GpsFixed as GpsFixedIcon
} from '@mui/icons-material';
import { Link as RouterLink, useLocation } from 'react-router-dom';

const drawerWidth = 240;

const StyledDrawer = styled(Drawer)({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    boxSizing: 'border-box',
  },
});

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Document Summarizer', icon: <SummarizeIcon />, path: '/summarizer' },
  { text: 'Q&A Generator', icon: <QuizIcon />, path: '/qa-generator' },
  { text: 'Flashcards', icon: <FlashOnIcon />, path: '/flashcards' },
  { text: 'Lecture Planner', icon: <ScheduleIcon />, path: '/lecture-planner' },
  { text: 'Content Gap Detector', icon: <GpsFixedIcon />, path: '/content-gap' },
  { text: 'Document Comparison', icon: <CompareArrowsIcon />, path: '/compare' },
  { text: 'Assignment Generator', icon: <AssignmentIcon />, path: '/assignment' },
];

const Sidebar = () => {
  const location = useLocation();

  return (
    <StyledDrawer variant="permanent">
      <Toolbar /> {/* This pushes content below the app bar */}
      <Box sx={{ overflow: 'auto' }}>
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.text}
              component={RouterLink}
              to={item.path}
              selected={location.pathname === item.path}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                  },
                },
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
      </Box>
    </StyledDrawer>
  );
};

export default Sidebar;
