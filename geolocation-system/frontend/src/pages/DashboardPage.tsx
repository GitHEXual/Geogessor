import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Paper,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  CloudUpload,
  LocationOn,
  Download,
  History,
} from '@mui/icons-material';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Загрузка изображений',
      description: 'Загрузите фотографии для распознавания координат',
      icon: <CloudUpload sx={{ fontSize: 40 }} />,
      path: '/upload',
      color: '#1976d2',
    },
    {
      title: 'Каталог координат',
      description: 'Просмотр и управление координатами зданий',
      icon: <LocationOn sx={{ fontSize: 40 }} />,
      path: '/coordinates',
      color: '#2e7d32',
    },
    {
      title: 'Экспорт данных',
      description: 'Экспорт результатов в различных форматах',
      icon: <Download sx={{ fontSize: 40 }} />,
      path: '/export',
      color: '#ed6c02',
    },
    {
      title: 'История запросов',
      description: 'Просмотр истории обработки изображений',
      icon: <History sx={{ fontSize: 40 }} />,
      path: '/history',
      color: '#9c27b0',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Панель управления
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Добро пожаловать в систему распознавания географических координат по фотографиям
      </Typography>

      <Grid container spacing={3}>
        {features.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <Box sx={{ color: feature.color, mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" component="h2" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {feature.description}
                </Typography>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => navigate(feature.path)}
                  sx={{ mt: 2 }}
                >
                  Перейти
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ mt: 4, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Статистика системы
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                0
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Обработано изображений
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                0
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Найдено зданий
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                0
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Определено координат
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={3}>
            <Box textAlign="center">
              <Typography variant="h4" color="primary">
                0
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Экспортировано файлов
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};
