import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, AppBar, Toolbar, Typography, Box, Tabs, Tab, Container } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SportsIcon from '@mui/icons-material/Sports';
import theme from './theme/theme';
import Chat from './pages/Chat';
import Dashboard from './pages/Dashboard';
import Opportunities from './pages/Opportunities';

function Navigation() {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <AppBar position="static" elevation={0}>
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          <Typography
            variant="h5"
            sx={{
              flexGrow: 1,
              fontWeight: 700,
              color: 'white',
              textDecoration: 'none',
            }}
          >
            🎯 BetIQ
          </Typography>

          <Tabs
            value={currentPath}
            textColor="inherit"
            TabIndicatorProps={{
              style: { backgroundColor: 'white' },
            }}
          >
            <Tab
              label="Oportunidades"
              icon={<SportsIcon />}
              iconPosition="start"
              value="/"
              component={Link}
              to="/"
              sx={{ color: 'white', minHeight: 64 }}
            />
            <Tab
              label="Chat"
              icon={<ChatIcon />}
              iconPosition="start"
              value="/chat"
              component={Link}
              to="/chat"
              sx={{ color: 'white', minHeight: 64 }}
            />
            <Tab
              label="Dashboard"
              icon={<DashboardIcon />}
              iconPosition="start"
              value="/dashboard"
              component={Link}
              to="/dashboard"
              sx={{ color: 'white', minHeight: 64 }}
            />
          </Tabs>
        </Toolbar>
      </Container>
    </AppBar>
  );
}

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
          <Navigation />
          <Routes>
            <Route path="/" element={<Opportunities />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;