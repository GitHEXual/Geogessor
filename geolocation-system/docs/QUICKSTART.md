# Быстрый старт

## Предварительные требования

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (для разработки frontend)
- Python 3.9+ (для разработки backend)
- Kubernetes 1.20+ (опционально)

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd geolocation-system
```

### 2. Настройка окружения

```bash
# Копирование файла конфигурации
cp env.example .env

# Редактирование конфигурации
nano .env
```

Обновите следующие параметры в `.env`:
- `GOOGLE_API_KEY` - ваш Google API ключ
- `SECRET_KEY` - безопасный JWT секретный ключ
- `POSTGRES_PASSWORD` - пароль для PostgreSQL

### 3. Запуск системы

```bash
# Запуск всех сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 4. Доступ к приложению

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 5. Первый вход

1. Откройте http://localhost:3000
2. Войдите с учетными данными:
   - Логин: `admin`
   - Пароль: `admin`

## Тестирование

### Запуск тестов

```bash
# Установка зависимостей для тестов
pip install -r tests/requirements.txt

# Запуск тестов
python -m pytest tests/ -v
```

### Тестирование API

```bash
# Проверка здоровья API
curl http://localhost:8000/health

# Аутентификация
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

## Разработка

### Frontend разработка

```bash
cd frontend
npm install
npm start
```

### Backend разработка

```bash
# Установка зависимостей для каждого сервиса
cd backend/api-gateway
pip install -r requirements.txt

# Запуск сервиса
uvicorn app.main:app --reload --port 8000
```

### ML модели

```bash
cd ml-models
pip install -r requirements.txt

# Обучение модели
python cvm-net/training.py
```

## Мониторинг

### Prometheus

```bash
# Запуск Prometheus
docker run -d -p 9090:9090 \
  -v $(pwd)/infrastructure/monitoring/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### Grafana

```bash
# Запуск Grafana
docker run -d -p 3001:3000 grafana/grafana
```

## Развертывание в Kubernetes

```bash
# Применение манифестов
kubectl apply -f infrastructure/kubernetes/

# Проверка статуса
kubectl get pods -n geolocation-system
```

## Устранение неполадок

### Проблемы с Docker

```bash
# Очистка контейнеров
docker-compose down
docker system prune -a

# Перезапуск
docker-compose up -d
```

### Проблемы с базой данных

```bash
# Подключение к PostgreSQL
docker exec -it geolocation-system_postgres_1 psql -U postgres -d geolocation_db
```

### Логи сервисов

```bash
# Просмотр логов
docker-compose logs -f [service-name]

# Примеры:
docker-compose logs -f api-gateway
docker-compose logs -f neural-service
```

## Производительность

### Оптимизация для продакшена

1. **Масштабирование сервисов**:
   ```yaml
   # В docker-compose.yml
   deploy:
     replicas: 3
   ```

2. **Кэширование**:
   - Redis для кэширования результатов
   - CDN для статических файлов

3. **Мониторинг**:
   - Prometheus + Grafana
   - ELK Stack для логов

### Рекомендации по ресурсам

- **Минимум**: 4 CPU, 8GB RAM
- **Рекомендуется**: 8 CPU, 16GB RAM
- **GPU**: Для neural-service (опционально)

## Безопасность

### Настройка HTTPS

```bash
# Генерация SSL сертификатов
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### Настройка файрвола

```bash
# Разрешение только необходимых портов
ufw allow 80
ufw allow 443
ufw allow 22
```

## Поддержка

- **Документация**: `docs/`
- **Issues**: GitHub Issues
- **Логи**: `docker-compose logs`
