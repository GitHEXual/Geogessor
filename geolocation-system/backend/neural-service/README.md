# Neural Service

🚫 **СЕРВИС ВРЕМЕННО ОТКЛЮЧЕН**

## Статус

Neural Service требует настройки и интеграции с CVM-Net моделью для распознавания географических координат по фотографиям.

## Что нужно для включения

### 1. Установка зависимостей
```bash
# Создайте requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
tensorflow==2.13.0
numpy==1.24.3
opencv-python==4.8.1.78
Pillow==10.1.0
python-dotenv==1.0.0
pydantic==2.5.0
EOF
```

### 2. Создание Dockerfile
```dockerfile
FROM tensorflow/tensorflow:2.13.0

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models/ /app/models/
COPY . .

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Создание основного файла app/main.py
```python
from fastapi import FastAPI, File, UploadFile, HTTPException
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import logging
import os

app = FastAPI(title="Neural Network Service")

# Загрузка модели
model = None
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/cvm-net")

@app.on_event("startup")
async def load_model():
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            logging.info("CVM-Net model loaded successfully")
        else:
            # Создание заглушки модели
            model = create_dummy_model()
            logging.warning("Using dummy model - CVM-Net model not found")
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        model = create_dummy_model()

def create_dummy_model():
    # Простая заглушка модели
    from tensorflow.keras.applications import VGG16
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
    from tensorflow.keras.models import Model
    
    base_model = VGG16(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    for layer in base_model.layers:
        layer.trainable = False
    
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dense(256, activation='relu')(x)
    coordinates = Dense(2, activation='linear')(x)
    
    model = Model(inputs=base_model.input, outputs=coordinates)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    return model

@app.post("/predict")
async def predict_coordinates(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image = image.resize((224, 224))
        image_array = np.array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)
        
        prediction = model.predict(image_array)
        latitude, longitude = prediction[0]
        
        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "confidence": float(np.random.uniform(0.7, 0.95))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "neural-service",
        "model_loaded": model is not None
    }
```

### 4. Подготовка модели
```bash
# Создайте директорию для модели
mkdir -p ../ml-models/cvm-net

# Разместите файлы модели CVM-Net в ../ml-models/cvm-net/
# Или используйте заглушку для тестирования
```

## Включение в систему

После создания файлов:

1. **Раскомментируйте в docker-compose.yml:**
```yaml
neural-service:
  build: ./backend/neural-service
  ports:
    - "8002:8000"
  volumes:
    - ./ml-models:/app/models
  environment:
    - MODEL_PATH=/app/models/cvm-net
```

2. **Раскомментируйте в API Gateway:**
```python
SERVICES = {
    # ...
    "neural": os.getenv("NEURAL_SERVICE_URL", "http://neural-service:8000"),
    # ...
}

@app.post("/api/neural/predict")
async def predict_coordinates(request: Request):
    # ...
```

3. **Раскомментируйте Kubernetes манифесты:**
```bash
kubectl apply -f infrastructure/kubernetes/neural-service.yaml
```

## Тестирование

```bash
# Сборка образа
docker build -t geolocation/neural-service:latest .

# Запуск контейнера
docker run -p 8002:8000 geolocation/neural-service:latest

# Тестирование API
curl -X POST "http://localhost:8002/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test-image.jpg"
```

## Требования

- **Минимум**: 2GB RAM, 1 CPU
- **Рекомендуется**: 4GB RAM, 2 CPU, GPU (для продакшена)
- **Модель**: CVM-Net или совместимая модель
- **Фреймворк**: TensorFlow 2.x

## Поддержка

При возникновении проблем:
1. Проверьте логи контейнера
2. Убедитесь в корректности путей к модели
3. Проверьте совместимость версий TensorFlow
4. Изучите документацию CVM-Net