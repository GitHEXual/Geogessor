# Система распознавания географических координат по фотографиям

Микросервисное веб-приложение для автоматического определения географических координат объектов по фотографиям с использованием нейросетевых технологий.

## Архитектура

- **Frontend**: React 18+ с TypeScript
- **Backend**: Python 3.9+ с FastAPI
- **ML**: TensorFlow 2.x с CVM-Net моделью
- **Инфраструктура**: Docker + Kubernetes

## Быстрый старт

```bash
# Клонирование репозитория
git clone <repository-url>
cd geolocation-system

# Запуск локальной разработки
docker-compose up -d

# Доступ к приложению
# Frontend: http://localhost:3000
# API Gateway: http://localhost:8000
```

## Структура проекта

```
geolocation-system/
├── frontend/                 # React приложение
├── backend/                 # Микросервисы
├── ml-models/              # Модели машинного обучения
├── infrastructure/         # Инфраструктура
├── docs/                  # Документация
├── tests/                 # Тесты
└── docker-compose.yml     # Локальная разработка
```

## Сервисы

1. **API Gateway** - Маршрутизация запросов
2. **Auth Service** - Аутентификация и авторизация
3. **Image Processing Service** - Обработка изображений
4. **Neural Network Service** - CVM-Net модель
5. **Coordinates Service** - Работа с координатами
6. **Export Service** - Экспорт данных
7. **Notification Service** - Уведомления

## Требования

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+
- Python 3.9+
- Kubernetes 1.20+ (для продакшена)

## Лицензия

MIT License
