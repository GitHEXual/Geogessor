import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Button,
  Box,
  Menu,
  MenuItem,
  IconButton,
  Typography,
} from '@mui/material';
import {
  AccountCircle,
  Dashboard,
  CloudUpload,
  LocationOn,
  Download,
  History,
  Logout,
} from '@mui/icons-material';
import { useAuth } from '../hooks/useAuth';

export const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
  };

  const navigationItems = [
    { path: '/', label: 'Панель', icon: <Dashboard /> },
    { path: '/upload', label: 'Загрузка', icon: <CloudUpload /> },
    { path: '/coordinates', label: 'Координаты', icon: <LocationOn /> },
    { path: '/export', label: 'Экспорт', icon: <Download /> },
    { path: '/history', label: 'История', icon: <History /> },
  ];

  return (
    <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
      {navigationItems.map((item) => (
        <Button
          key={item.path}
          color="inherit"
          startIcon={item.icon}
          onClick={() => navigate(item.path)}
          sx={{
            mx: 1,
            bgcolor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
          }}
        >
          {item.label}
        </Button>
      ))}

      <Box sx={{ flexGrow: 1 }} />

      <Typography variant="body2" sx={{ mr: 2 }}>
        {user?.username}
      </Typography>

      <IconButton
        size="large"
                aria-label="account of current user"
        aria-controls="menu-appbar"
        aria-haspopup="true"
        onClick={handleMenu}
        color="inherit"
      >
        <AccountCircle />
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={handleLogout}>
          <Logout sx={{ mr: 1 }} />
          Выйти
        </MenuItem>
      </Menu>
    </Box>
  );
};
