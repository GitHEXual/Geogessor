# Image Recognition Service - Web Application

Веб-приложение для распознавания координат объектов с аэрофотоснимков.

## Архитектура

Проект состоит из микросервисов:
- **Backend** - ASP.NET Core 9 Web API
- **Frontend** - React + TypeScript + Vite
- **PostgreSQL** - База данных
- **MinIO** - Объектное хранилище для изображений

## Технологический стек

### Backend
- .NET 9
- ASP.NET Core Web API
- Entity Framework Core
- PostgreSQL (Npgsql)
- MinIO SDK
- JWT Authentication

### Frontend
- React 18
- TypeScript
- Vite
- TailwindCSS
- React Router
- Axios

## Порты

- **Frontend**: `4200`
- **Backend API**: `4100`
- **PostgreSQL**: `4300`
- **MinIO API**: `4400`
- **MinIO Console**: `4401`

## Быстрый старт

### Требования
- Docker
- Docker Compose

### Запуск проекта

```bash
# Клонировать репозиторий и перейти в директорию
cd /home/maximally/Univer/GroupProject

# Запустить все сервисы
docker-compose up --build

# Или в фоновом режиме
docker-compose up --build -d
```

### Остановка

```bash
docker-compose down

# С удалением volumes (БД и хранилище)
docker-compose down -v
```

## Доступ к сервисам

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:4100
- **Swagger UI**: http://localhost:4100/swagger
- **MinIO Console**: http://localhost:4401
  - Username: `minioadmin`
  - Password: `minioadmin123`

## Учетные данные по умолчанию

### PostgreSQL
- Database: `imagerecognition`
- Username: `admin`
- Password: `admin123`

### MinIO
- Access Key: `minioadmin`
- Secret Key: `minioadmin123`
- Bucket: `images`

### Администратор приложения
После первого запуска создается администратор:
- Email: `admin@admin.com`
- Password: `Admin123!`

## Структура проекта

```
.
├── backend/                  # .NET 9 Web API
│   ├── src/
│   │   ├── API/             # Controllers, Middleware
│   │   ├── Application/     # Business Logic, Services, DTOs
│   │   ├── Domain/          # Entities, Enums
│   │   └── Infrastructure/  # EF Core, Repositories, MinIO
│   └── Dockerfile
├── frontend/                # React + TypeScript
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API clients
│   │   └── ...
│   └── Dockerfile
└── docker-compose.yml
```

## Разработка

### Backend (локально)

```bash
cd backend/src/API
dotnet restore
dotnet run
```

### Frontend (локально)

```bash
cd frontend
npm install
npm run dev
```

## Ветки Git

- `main` - основная ветка
- `backend/dev` - разработка backend
- `frontend/dev` - разработка frontend

## Функционал

### MVP v1.0
- ✅ Регистрация и авторизация (JWT)
- ✅ Управление изображениями (загрузка, просмотр, удаление)
- ✅ Роли пользователей (User, Admin)
- ✅ Админ-панель (управление пользователями, баны)
- ✅ Удаление собственного аккаунта

### Планируется
- Интеграция с микросервисом нейронной сети
- Визуализация результатов распознавания
- Экспорт координат объектов
- Аналитика и отчеты

## Лицензия

Учебный проект для университета.

