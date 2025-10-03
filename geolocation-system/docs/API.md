# API Документация

## Базовый URL

```
http://localhost:8000
```

## Аутентификация

Все API запросы (кроме `/health` и `/auth/login`) требуют JWT токен в заголовке:

```
Authorization: Bearer <your-jwt-token>
```

## Эндпоинты

### 1. Проверка здоровья

```http
GET /health
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.0,
  "services": {
    "auth": "available",
    "image": "available",
    "neural": "available",
    "coordinates": "available",
    "export": "available",
    "notification": "available"
  }
}
```

### 2. Аутентификация

#### Вход в систему

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin"
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Получение информации о пользователе

```http
GET /auth/me
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "role": "admin"
}
```

#### Регистрация

```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123"
}
```

### 3. Обработка изображений

#### Загрузка и детекция зданий

```http
POST /api/images/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image-file>
```

**Ответ:**
```json
{
  "image_id": "uuid-string",
  "buildings": [
    {
      "id": 0,
      "bbox": [100, 150, 300, 400],
      "confidence": 0.95,
      "cropped_image": "base64-encoded-image",
      "filename": "building_0_image.jpg"
    }
  ],
  "total_detected": 1
}
```

#### Предобработка изображения

```http
POST /api/images/preprocess
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image-file>
```

**Ответ:**
```json
{
  "processed_image": "base64-encoded-image"
}
```

### 4. Нейросетевое предсказание (недоступно)

> **Примечание:** Neural Service временно отключен и требует настройки модели.

#### Предсказание координат

```http
POST /api/neural/predict
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <image-file>
```

**Ответ (когда сервис будет доступен):**
```json
{
  "latitude": 55.7558,
  "longitude": 37.6176,
  "confidence": 0.87
}
```

### 5. Работа с координатами

#### Получение адреса по координатам

```http
POST /api/coordinates/address
Authorization: Bearer <token>
Content-Type: application/json

{
  "latitude": 55.7558,
  "longitude": 37.6176
}
```

**Ответ:**
```json
{
  "street": "Красная площадь",
  "city": "Москва",
  "country": "Россия",
  "postal_code": "109012",
  "full_address": "Красная площадь, Москва, Россия"
}
```

#### Получение Street View изображения

```http
POST /api/coordinates/street-view
Authorization: Bearer <token>
Content-Type: application/json

{
  "latitude": 55.7558,
  "longitude": 37.6176,
  "heading": 0
}
```

**Ответ:**
```json
{
  "image_data": "base64-encoded-image",
  "metadata": {
    "status": "OK",
    "copyright": "©2023 Google"
  }
}
```

#### Расчет расстояния между точками

```http
POST /api/coordinates/calculate-distance
Authorization: Bearer <token>
Content-Type: application/json

{
  "coord1": {
    "latitude": 55.7558,
    "longitude": 37.6176
  },
  "coord2": {
    "latitude": 55.7522,
    "longitude": 37.6156
  }
}
```

**Ответ:**
```json
{
  "distance_km": 0.5
}
```

### 6. Экспорт данных

#### Экспорт в XLSX

```http
POST /api/export/xlsx
Authorization: Bearer <token>
Content-Type: application/json

{
  "data": [
    {
      "building_id": "uuid-1",
      "coordinates": {
        "latitude": 55.7558,
        "longitude": 37.6176
      },
      "address": "Москва, Россия",
      "confidence": 0.95,
      "timestamp": "2023-01-01T12:00:00Z"
    }
  ]
}
```

**Ответ:** XLSX файл для скачивания

#### Экспорт изображений в ZIP

```http
POST /api/export/images
Authorization: Bearer <token>
Content-Type: application/json

{
  "images": [
    {
      "image": "base64-encoded-image",
      "coordinates": "55.7558,37.6176",
      "filename": "building_1.jpg"
    }
  ]
}
```

**Ответ:** ZIP архив для скачивания

### 7. Уведомления

#### Отправка уведомления

```http
POST /api/notifications/send
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": 1,
  "title": "Обработка завершена",
  "message": "Ваше изображение успешно обработано",
  "type": "success"
}
```

#### Получение уведомлений пользователя

```http
GET /api/notifications/user/{user_id}?limit=50
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "user_id": 1,
      "title": "Обработка завершена",
      "message": "Ваше изображение успешно обработано",
      "type": "success",
      "timestamp": "2023-01-01T12:00:00Z",
      "read": false
    }
  ]
}
```

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 400 | Неверный запрос |
| 401 | Не авторизован |
| 403 | Доступ запрещен |
| 404 | Не найдено |
| 429 | Превышен лимит запросов |
| 500 | Внутренняя ошибка сервера |
| 503 | Сервис недоступен |
| 504 | Таймаут сервиса |

## Примеры использования

### Python

```python
import requests

# Аутентификация
response = requests.post('http://localhost:8000/auth/login', json={
    'username': 'admin',
    'password': 'admin'
})
token = response.json()['access_token']

# Загрузка изображения
headers = {'Authorization': f'Bearer {token}'}
with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/images/upload', 
                           files=files, headers=headers)
    result = response.json()
    print(f"Найдено зданий: {result['total_detected']}")
```

### JavaScript

```javascript
// Аутентификация
const loginResponse = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: 'admin', password: 'admin'})
});
const {access_token} = await loginResponse.json();

// Загрузка изображения
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:8000/api/images/upload', {
    method: 'POST',
    headers: {'Authorization': `Bearer ${access_token}`},
    body: formData
});
const result = await uploadResponse.json();
console.log(`Найдено зданий: ${result.total_detected}`);
```

### cURL

```bash
# Аутентификация
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  | jq -r '.access_token')

# Загрузка изображения
curl -X POST http://localhost:8000/api/images/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@image.jpg"
```

## Rate Limiting

API имеет ограничения на количество запросов:
- **100 запросов в минуту** на IP адрес
- **1000 запросов в час** на пользователя

При превышении лимита возвращается ошибка 429.

## WebSocket (планируется)

```javascript
// Подключение к WebSocket для real-time уведомлений
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    console.log('Уведомление:', notification);
};
```
