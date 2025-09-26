import React, { useState, useCallback } from 'react';
import {
  Container,
  Paper,
  Typography,
  Button,
  Box,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardMedia,
  CardContent,
  Chip,
} from '@mui/material';
import { CloudUpload, Delete } from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';

interface UploadedImage {
  file: File;
  preview: string;
  id: string;
}

interface Building {
  id: number;
  bbox: number[];
  confidence: number;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  address: string;
}

export const ImageUploadPage: React.FC = () => {
  const [images, setImages] = useState<UploadedImage[]>([]);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newImages = acceptedFiles.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
      id: Math.random().toString(36).substr(2, 9),
    }));
    setImages((prev) => [...prev, ...newImages]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
    },
    multiple: true,
  });

  const removeImage = (id: string) => {
    setImages((prev) => {
      const image = prev.find((img) => img.id === id);
      if (image) {
        URL.revokeObjectURL(image.preview);
      }
      return prev.filter((img) => img.id !== id);
    });
  };

  const processImages = async () => {
    if (images.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      images.forEach((image) => {
        formData.append('files', image.file);
      });

      const response = await fetch('/api/images/upload', {
        method: 'POST',
        body: formData,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка обработки изображений');
      }

      const result = await response.json();
      setBuildings(result.buildings || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" component="h1" gutterBottom>
        Загрузка изображений
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box
          {...getRootProps()}
          sx={{
            border: '2px dashed #ccc',
            borderRadius: 2,
            p: 4,
            textAlign: 'center',
            cursor: 'pointer',
            bgcolor: isDragActive ? 'action.hover' : 'background.paper',
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          <input {...getInputProps()} />
          <CloudUpload sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive
              ? 'Отпустите файлы здесь...'
              : 'Перетащите изображения сюда или нажмите для выбора'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Поддерживаются форматы: JPEG, PNG, JPG
          </Typography>
        </Box>

        {images.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Загружено изображений: {images.length}
              </Typography>
              <Button
                variant="contained"
                onClick={processImages}
                disabled={loading}
                startIcon={loading ? <LinearProgress /> : <CloudUpload />}
              >
                {loading ? 'Обработка...' : 'Обработать изображения'}
              </Button>
            </Box>

            <Grid container spacing={2}>
              {images.map((image) => (
                <Grid item xs={12} sm={6} md={4} key={image.id}>
                  <Card>
                    <CardMedia
                      component="img"
                      height="200"
                      image={image.preview}
                      alt="Uploaded"
                    />
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        {image.file.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {(image.file.size / 1024 / 1024).toFixed(2)} MB
                      </Typography>
                      <Button
                        size="small"
                        color="error"
                        startIcon={<Delete />}
                        onClick={() => removeImage(image.id)}
                        sx={{ mt: 1 }}
                      >
                        Удалить
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {buildings.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Результаты распознавания
          </Typography>
          <Grid container spacing={2}>
            {buildings.map((building) => (
              <Grid item xs={12} sm={6} md={4} key={building.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Здание #{building.id + 1}
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={`Уверенность: ${(building.confidence * 100).toFixed(1)}%`}
                        color={building.confidence > 0.8 ? 'success' : 'warning'}
                        size="small"
                      />
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Координаты:</strong><br />
                      Широта: {building.coordinates.latitude.toFixed(6)}<br />
                      Долгота: {building.coordinates.longitude.toFixed(6)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      <strong>Адрес:</strong><br />
                      {building.address}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Paper>
      )}
    </Container>
  );
};
