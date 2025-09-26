import React from 'react';
import { RouteObject } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { ImageUploadPage } from './pages/ImageUploadPage';
import { CoordinatesPage } from './pages/CoordinatesPage';
import { ExportPage } from './pages/ExportPage';
import { HistoryPage } from './pages/HistoryPage';
import { ProtectedRoute } from './components/ProtectedRoute';

export const Routes: RouteObject[] = [
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/upload',
    element: (
      <ProtectedRoute>
        <ImageUploadPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/coordinates',
    element: (
      <ProtectedRoute>
        <CoordinatesPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/export',
    element: (
      <ProtectedRoute>
        <ExportPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/history',
    element: (
      <ProtectedRoute>
        <HistoryPage />
      </ProtectedRoute>
    ),
  },
];
