#!/bin/bash

# Скрипт сборки Docker образов для системы геолокации

set -e

echo "🔨 Сборка Docker образов для системы геолокации..."

# Frontend
echo "📦 Сборка frontend..."
docker build -t geolocation/frontend:latest ./frontend/

# Backend services (без neural-service)
for service in api-gateway auth-service image-service coordinates-service export-service notification-service; do
    echo "📦 Сборка $service..."
    docker build -t geolocation/$service:latest ./backend/$service/
done

echo "✅ Все образы собраны успешно!"
echo ""
echo "📋 Список созданных образов:"
docker images | grep geolocation

echo ""
echo "ℹ️  Примечание: Neural Service не собран - требует настройки модели"
echo "   Для сборки neural-service выполните:"
echo "   docker build -t geolocation/neural-service:latest ./backend/neural-service/"
