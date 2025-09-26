# Руководство по разработке микросервисного веб-приложения с модулем нейросети для распознавания географических координат

## Содержание
1. [Обзор проекта](#обзор-проекта)
2. [Архитектура системы](#архитектура-системы)
3. [Технологический стек](#технологический-стек)
4. [Структура проекта](#структура-проекта)
5. [Реализация компонентов](#реализация-компонентов)
6. [Интеграция с внешними сервисами](#интеграция-с-внешними-сервисами)
7. [Развертывание](#развертывание)
8. [API документация](#api-документация)
9. [Безопасность](#безопасность)
10. [Мониторинг и логирование](#мониторинг-и-логирование)

## Обзор проекта

### Цель проекта
Разработка микросервисного веб-приложения для автоматического определения географических координат объектов по фотографиям с использованием нейросетевых технологий и интеграции с Google Street View API.

### Основные задачи
1. **Распознавание зданий**: Алгоритмы для определения bbox и выделения объектов на фотографиях
2. **Веб-интерфейс загрузки**: Система для загрузки фотоматериалов и отображения результатов
3. **Каталог координат**: Интерфейс для загрузки координат и получения снимков зданий
4. **Интеграция**: API для интеграции с внешними системами
5. **Экспорт данных**: Функции экспорта в XLSX и изображений зданий
6. **Система авторизации**: Разграничение прав доступа и управление пользователями

## Архитектура системы

### Микросервисная архитектура

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Auth Service  │
│   (React/Vue)   │◄──►│   (Kong/Nginx)  │◄──►│   (JWT/OAuth)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │ Image        │ │ Neural    │ │ Coordinates │
        │ Processing   │ │ Network   │ │ Service     │
        │ Service      │ │ Service   │ │             │
        └──────────────┘ └───────────┘ └─────────────┘
                │               │               │
        ┌───────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
        │ File Storage │ │ Model     │ │ Google      │
        │ (MinIO/S3)   │ │ Storage   │ │ Street View │
        └──────────────┘ └───────────┘ └─────────────┘
```

### Компоненты системы

1. **Frontend Service** - Веб-интерфейс пользователя
2. **API Gateway** - Маршрутизация и балансировка нагрузки
3. **Auth Service** - Аутентификация и авторизация
4. **Image Processing Service** - Обработка и подготовка изображений
5. **Neural Network Service** - Модель CVM-Net для распознавания
6. **Coordinates Service** - Работа с географическими данными
7. **Export Service** - Экспорт данных в различные форматы
8. **Notification Service** - Уведомления пользователей

## Технологический стек

### Backend
- **Язык**: Python 3.9+
- **Фреймворк**: FastAPI
- **База данных**: PostgreSQL + Redis
- **ORM**: SQLAlchemy
- **Контейнеризация**: Docker + Docker Compose
- **Очереди**: Celery + Redis
- **Файловое хранилище**: MinIO (S3-совместимое)

### Frontend
- **Фреймворк**: React 18+ с TypeScript
- **UI библиотека**: Material-UI или Ant Design
- **Состояние**: Redux Toolkit
- **HTTP клиент**: Axios
- **Карты**: Google Maps API

### Machine Learning
- **Фреймворк**: TensorFlow 2.x / PyTorch
- **Модель**: CVM-Net (Cross-View Matching Network)
- **Предобработка**: OpenCV, PIL
- **Инференс**: TensorFlow Serving / TorchServe

### Инфраструктура
- **Оркестрация**: Kubernetes / Docker Swarm
- **Мониторинг**: Prometheus + Grafana
- **Логирование**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **CI/CD**: GitLab CI / GitHub Actions

## Структура проекта

```
project/
├── frontend/                 # React приложение
│   ├── src/
│   │   ├── components/      # React компоненты
│   │   ├── pages/          # Страницы приложения
│   │   ├── services/       # API сервисы
│   │   ├── store/          # Redux store
│   │   └── utils/          # Утилиты
│   ├── public/
│   └── package.json
│
├── backend/                 # Микросервисы
│   ├── api-gateway/        # API Gateway
│   ├── auth-service/       # Сервис аутентификации
│   ├── image-service/      # Обработка изображений
│   ├── neural-service/     # Нейросетевая модель
│   ├── coordinates-service/ # Работа с координатами
│   ├── export-service/     # Экспорт данных
│   └── notification-service/ # Уведомления
│
├── ml-models/              # Модели машинного обучения
│   ├── cvm-net/           # CVM-Net модель
│   ├── preprocessing/     # Скрипты предобработки
│   └── training/          # Скрипты обучения
│
├── infrastructure/         # Инфраструктура
│   ├── docker/           # Docker конфигурации
│   ├── kubernetes/        # K8s манифесты
│   ├── monitoring/        # Конфигурации мониторинга
│   └── scripts/          # Скрипты развертывания
│
├── docs/                  # Документация
├── tests/                 # Тесты
└── docker-compose.yml     # Локальная разработка
```

## Реализация компонентов

### 1. Neural Network Service

#### Установка и настройка CVM-Net

```python
# neural-service/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import io
import logging

app = FastAPI(title="Neural Network Service")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка модели CVM-Net
model = None

@app.on_event("startup")
async def load_model():
    global model
    try:
        # Загрузка предобученной модели CVM-Net
        model = tf.keras.models.load_model('/app/models/cvm-net')
        logging.info("CVM-Net model loaded successfully")
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise

class ImageProcessor:
    def __init__(self):
        self.target_size = (224, 224)
    
    def preprocess_image(self, image_bytes: bytes) -> np.ndarray:
        """Предобработка изображения для CVM-Net"""
        # Загрузка изображения
        image = Image.open(io.BytesIO(image_bytes))
        
        # Конвертация в RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Изменение размера
        image = image.resize(self.target_size)
        
        # Нормализация
        image_array = np.array(image) / 255.0
        
        # Добавление batch dimension
        image_array = np.expand_dims(image_array, axis=0)
        
        return image_array

processor = ImageProcessor()

@app.post("/predict")
async def predict_coordinates(file: UploadFile = File(...)):
    """Предсказание координат по изображению"""
    try:
        # Чтение изображения
        image_bytes = await file.read()
        
        # Предобработка
        processed_image = processor.preprocess_image(image_bytes)
        
        # Предсказание
        prediction = model.predict(processed_image)
        
        # Извлечение координат (предполагаем, что модель возвращает [lat, lon])
        latitude, longitude = prediction[0]
        
        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "confidence": float(prediction[1]) if len(prediction) > 1 else 0.8
        }
    
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}
```

#### Dockerfile для Neural Service

```dockerfile
# neural-service/Dockerfile
FROM tensorflow/tensorflow:2.10.0-gpu

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копирование модели
COPY models/ /app/models/

# Копирование кода
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Image Processing Service

```python
# image-service/app/main.py
from fastapi import FastAPI, File, UploadFile, HTTPException
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Dict, Tuple

app = FastAPI(title="Image Processing Service")

class BuildingDetector:
    def __init__(self):
        # Загрузка модели для детекции зданий (YOLO, R-CNN и т.д.)
        pass
    
    def detect_buildings(self, image: np.ndarray) -> List[Dict]:
        """Детекция зданий на изображении"""
        # Здесь должна быть реализация детекции зданий
        # Возвращаем bbox координаты и confidence scores
        buildings = []
        
        # Пример детекции (заглушка)
        height, width = image.shape[:2]
        buildings.append({
            "bbox": [0.1 * width, 0.1 * height, 0.8 * width, 0.8 * height],
            "confidence": 0.95,
            "class": "building"
        })
        
        return buildings
    
    def crop_building(self, image: np.ndarray, bbox: List[int]) -> np.ndarray:
        """Обрезка здания по bbox"""
        x1, y1, x2, y2 = bbox
        return image[y1:y2, x1:x2]

detector = BuildingDetector()

@app.post("/detect-buildings")
async def detect_buildings(file: UploadFile = File(...)):
    """Детекция зданий на изображении"""
    try:
        # Чтение изображения
        image_bytes = await file.read()
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        # Детекция зданий
        buildings = detector.detect_buildings(image)
        
        # Обрезка каждого здания
        cropped_buildings = []
        for i, building in enumerate(buildings):
            cropped = detector.crop_building(image, building["bbox"])
            
            # Конвертация в base64 для передачи
            _, buffer = cv2.imencode('.jpg', cropped)
            cropped_base64 = base64.b64encode(buffer).decode('utf-8')
            
            cropped_buildings.append({
                "id": i,
                "bbox": building["bbox"],
                "confidence": building["confidence"],
                "cropped_image": cropped_base64
            })
        
        return {
            "buildings": cropped_buildings,
            "total_detected": len(buildings)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preprocess")
async def preprocess_image(file: UploadFile = File(...)):
    """Предобработка изображения для нейросети"""
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Конвертация в RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Изменение размера
        image = image.resize((224, 224))
        
        # Конвертация в base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        processed_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {"processed_image": processed_base64}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Coordinates Service

```python
# coordinates-service/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

app = FastAPI(title="Coordinates Service")

class Coordinates(BaseModel):
    latitude: float
    longitude: float
    confidence: Optional[float] = None

class Address(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    full_address: str

class CoordinatesService:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.geolocator = Nominatim(user_agent="coordinates_service")
    
    def get_address_from_coordinates(self, lat: float, lon: float) -> Address:
        """Получение адреса по координатам"""
        try:
            location = self.geolocator.reverse(f"{lat}, {lon}")
            if location:
                address_dict = location.raw.get('address', {})
                return Address(
                    street=address_dict.get('road'),
                    city=address_dict.get('city'),
                    country=address_dict.get('country'),
                    postal_code=address_dict.get('postcode'),
                    full_address=location.address
                )
        except Exception as e:
            print(f"Error getting address: {e}")
        
        return Address(full_address="Address not found")
    
    def get_street_view_image(self, lat: float, lon: float, heading: int = 0) -> str:
        """Получение Street View изображения"""
        try:
            url = f"https://maps.googleapis.com/maps/api/streetview"
            params = {
                "size": "640x640",
                "location": f"{lat},{lon}",
                "heading": heading,
                "key": self.google_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.content
            else:
                raise HTTPException(status_code=400, detail="Failed to get Street View image")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def calculate_distance(self, coord1: Coordinates, coord2: Coordinates) -> float:
        """Расчет расстояния между двумя точками"""
        point1 = (coord1.latitude, coord1.longitude)
        point2 = (coord2.latitude, coord2.longitude)
        return geodesic(point1, point2).kilometers

service = CoordinatesService()

@app.post("/get-address")
async def get_address(coordinates: Coordinates):
    """Получение адреса по координатам"""
    address = service.get_address_from_coordinates(
        coordinates.latitude, 
        coordinates.longitude
    )
    return address

@app.post("/get-street-view")
async def get_street_view(coordinates: Coordinates, heading: int = 0):
    """Получение Street View изображения"""
    image_data = service.get_street_view_image(
        coordinates.latitude,
        coordinates.longitude,
        heading
    )
    return {"image_data": image_data}

@app.post("/calculate-distance")
async def calculate_distance(coord1: Coordinates, coord2: Coordinates):
    """Расчет расстояния между точками"""
    distance = service.calculate_distance(coord1, coord2)
    return {"distance_km": distance}
```

### 4. Auth Service

```python
# auth-service/app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

app = FastAPI(title="Auth Service")

# Конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Зависимости
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class User:
    def __init__(self, id: int, username: str, email: str, role: str):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            # Здесь должна быть проверка пользователя в БД
            return User(id=1, username=username, email="user@example.com", role="user")
        except JWTError:
            return None

auth_service = AuthService()

@app.post("/login")
async def login(username: str, password: str):
    """Аутентификация пользователя"""
    # Здесь должна быть проверка в БД
    if username == "admin" and password == "admin":  # Заглушка
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

@app.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Получение информации о текущем пользователе"""
    token = credentials.credentials
    user = auth_service.verify_token(token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return user

@app.post("/register")
async def register(username: str, email: str, password: str):
    """Регистрация нового пользователя"""
    # Здесь должна быть логика регистрации
    hashed_password = auth_service.get_password_hash(password)
    # Сохранение в БД
    return {"message": "User registered successfully"}
```

### 5. Export Service

```python
# export-service/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import pandas as pd
import io
from typing import List, Dict
import zipfile
from PIL import Image
import base64

app = FastAPI(title="Export Service")

class ExportService:
    def export_to_xlsx(self, data: List[Dict]) -> bytes:
        """Экспорт данных в XLSX формат"""
        df = pd.DataFrame(data)
        
        # Создание Excel файла в памяти
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Coordinates', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def export_images_zip(self, images_data: List[Dict]) -> bytes:
        """Экспорт изображений в ZIP архив"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i, image_data in enumerate(images_data):
                # Декодирование base64 изображения
                image_bytes = base64.b64decode(image_data['image'])
                
                # Добавление в ZIP
                filename = f"building_{i+1}_{image_data.get('coordinates', 'unknown')}.jpg"
                zip_file.writestr(filename, image_bytes)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

export_service = ExportService()

@app.post("/export/xlsx")
async def export_xlsx(data: List[Dict]):
    """Экспорт данных в XLSX"""
    try:
        xlsx_data = export_service.export_to_xlsx(data)
        
        return StreamingResponse(
            io.BytesIO(xlsx_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=coordinates.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/images")
async def export_images(images_data: List[Dict]):
    """Экспорт изображений в ZIP"""
    try:
        zip_data = export_service.export_images_zip(images_data)
        
        return StreamingResponse(
            io.BytesIO(zip_data),
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=buildings_images.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Интеграция с внешними сервисами

### Google Street View API

```python
# Интеграция с Google Street View API
import requests
import os

class GoogleStreetViewAPI:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/streetview"
    
    def get_street_view_image(self, lat: float, lon: float, **kwargs):
        """Получение Street View изображения"""
        params = {
            "size": kwargs.get("size", "640x640"),
            "location": f"{lat},{lon}",
            "heading": kwargs.get("heading", 0),
            "pitch": kwargs.get("pitch", 0),
            "fov": kwargs.get("fov", 90),
            "key": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to get Street View image: {response.text}")
    
    def get_metadata(self, lat: float, lon: float):
        """Получение метаданных Street View"""
        metadata_url = "https://maps.googleapis.com/maps/api/streetview/metadata"
        params = {
            "location": f"{lat},{lon}",
            "key": self.api_key
        }
        
        response = requests.get(metadata_url, params=params)
        return response.json()
```

### Настройка CVM-Net модели

```python
# ml-models/cvm-net/setup.py
import tensorflow as tf
import numpy as np
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

class CVMModel:
    def __init__(self, input_shape=(224, 224, 3)):
        self.input_shape = input_shape
        self.model = self.build_model()
    
    def build_model(self):
        """Построение CVM-Net модели"""
        # Базовый VGG16
        base_model = VGG16(
            weights='imagenet',
            include_top=False,
            input_shape=self.input_shape
        )
        
        # Заморозка базовых слоев
        for layer in base_model.layers:
            layer.trainable = False
        
        # Добавление NetVLAD слоя
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        
        # Полносвязные слои для регрессии координат
        x = Dense(512, activation='relu')(x)
        x = Dense(256, activation='relu')(x)
        coordinates = Dense(2, activation='linear', name='coordinates')(x)
        
        # Создание модели
        model = Model(inputs=base_model.input, outputs=coordinates)
        
        return model
    
    def compile_model(self):
        """Компиляция модели"""
        self.model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
    
    def load_weights(self, weights_path):
        """Загрузка весов модели"""
        self.model.load_weights(weights_path)
    
    def predict(self, image):
        """Предсказание координат"""
        return self.model.predict(image)
```

## Развертывание

### Docker Compose для локальной разработки

```yaml
# docker-compose.yml
version: '3.8'

services:
  # База данных
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: geolocation_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  # MinIO для файлового хранилища
  minio:
    image: minio/minio
    command: server /data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  # API Gateway
  api-gateway:
    build: ./backend/api-gateway
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/geolocation_db
      - REDIS_URL=redis://redis:6379

  # Auth Service
  auth-service:
    build: ./backend/auth-service
    ports:
      - "8001:8000"
    depends_on:
      - postgres
    environment:
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/geolocation_db

  # Neural Network Service
  neural-service:
    build: ./backend/neural-service
    ports:
      - "8002:8000"
    volumes:
      - ./ml-models:/app/models
    environment:
      - MODEL_PATH=/app/models/cvm-net

  # Image Processing Service
  image-service:
    build: ./backend/image-service
    ports:
      - "8003:8000"
    depends_on:
      - minio

  # Coordinates Service
  coordinates-service:
    build: ./backend/coordinates-service
    ports:
      - "8004:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}

  # Export Service
  export-service:
    build: ./backend/export-service
    ports:
      - "8005:8000"

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api-gateway

volumes:
  postgres_data:
  minio_data:
```

### Kubernetes манифесты

```yaml
# infrastructure/kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: geolocation-system

---
# infrastructure/kubernetes/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: geolocation-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: geolocation_db
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: geolocation-system
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

## API документация

### Основные эндпоинты

#### 1. Аутентификация
```
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### 2. Загрузка и обработка изображений
```
POST /api/images/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

FormData:
- file: <image_file>
- workspace_id: <workspace_id>

Response:
{
  "image_id": "uuid",
  "buildings": [
    {
      "id": 0,
      "bbox": [x1, y1, x2, y2],
      "confidence": 0.95,
      "coordinates": {
        "latitude": 55.7558,
        "longitude": 37.6176
      },
      "address": "Moscow, Russia"
    }
  ]
}
```

#### 3. Получение Street View изображений
```
POST /api/coordinates/street-view
Authorization: Bearer <token>
Content-Type: application/json

{
  "latitude": 55.7558,
  "longitude": 37.6176,
  "heading": 0
}

Response:
{
  "image_data": "base64_encoded_image",
  "metadata": {
    "status": "OK",
    "copyright": "©2023 Google"
  }
}
```

#### 4. Экспорт данных
```
POST /api/export/xlsx
Authorization: Bearer <token>
Content-Type: application/json

{
  "data": [
    {
      "building_id": "uuid",
      "coordinates": {
        "latitude": 55.7558,
        "longitude": 37.6176
      },
      "address": "Moscow, Russia",
      "confidence": 0.95
    }
  ]
}

Response: XLSX file download
```

## Безопасность

### 1. Аутентификация и авторизация
- JWT токены с коротким временем жизни
- Refresh токены для обновления сессий
- Роли пользователей (admin, user, viewer)
- Rate limiting для API эндпоинтов

### 2. Защита данных
- Шифрование чувствительных данных в БД
- HTTPS для всех соединений
- Валидация входных данных
- Санитизация пользовательского ввода

### 3. Безопасность API
```python
# Пример middleware для безопасности
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from collections import defaultdict

# Rate limiting
request_counts = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Очистка старых запросов (старше 1 минуты)
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < 60
    ]
    
    # Проверка лимита (100 запросов в минуту)
    if len(request_counts[client_ip]) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

app.add_middleware(rate_limit_middleware)
```

## Мониторинг и логирование

### 1. Логирование
```python
# Настройка логирования
import logging
import sys
from pythonjsonlogger import jsonlogger

# Настройка JSON логгера
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Использование в сервисах
logger.info("User uploaded image", extra={
    "user_id": user_id,
    "image_size": image_size,
    "service": "image-service"
})
```

### 2. Мониторинг
```yaml
# Prometheus конфигурация
# infrastructure/monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'geolocation-services'
    static_configs:
      - targets: ['api-gateway:8000', 'neural-service:8000', 'image-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### 3. Health Checks
```python
# Пример health check для сервиса
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "model": await check_model_loaded(),
        "storage": await check_storage_connection()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Заключение

Данное руководство предоставляет полную структуру для разработки микросервисного веб-приложения с модулем нейросети для распознавания географических координат. Система включает в себя:

1. **Модульную архитектуру** с разделением ответственности
2. **Интеграцию с CVM-Net** для точного распознавания координат
3. **Google Street View API** для получения спутниковых снимков
4. **Систему авторизации** с разграничением прав доступа
5. **Функции экспорта** данных в различных форматах
6. **Масштабируемость** через микросервисную архитектуру
7. **Безопасность** и мониторинг системы

Следуя данному руководству, можно создать полнофункциональную систему для автоматического определения географических координат объектов по фотографиям с высокой точностью и удобным пользовательским интерфейсом.
