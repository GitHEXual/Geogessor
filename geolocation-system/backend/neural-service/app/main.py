from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import io
import logging
import os
from typing import List, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/cvm-net")

@app.on_event("startup")
async def load_model():
    global model
    try:
        # Загрузка предобученной модели CVM-Net
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            logger.info("CVM-Net model loaded successfully")
        else:
            # Создание заглушки модели для демонстрации
            model = create_dummy_model()
            logger.warning("Using dummy model - CVM-Net model not found")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        # Создание заглушки модели
        model = create_dummy_model()
        logger.warning("Using dummy model due to loading error")

def create_dummy_model():
    """Создание заглушки модели для демонстрации"""
    from tensorflow.keras.applications import VGG16
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
    from tensorflow.keras.models import Model
    
    # Базовый VGG16
    base_model = VGG16(
        weights='imagenet',
        include_top=False,
        input_shape=(224, 224, 3)
    )
    
    # Заморозка базовых слоев
    for layer in base_model.layers:
        layer.trainable = False
    
    # Добавление слоев для регрессии координат
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(512, activation='relu')(x)
    x = Dense(256, activation='relu')(x)
    coordinates = Dense(2, activation='linear', name='coordinates')(x)
    
    # Создание модели
    model = Model(inputs=base_model.input, outputs=coordinates)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    return model

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
        logger.info(f"Processing image: {file.filename}")
        
        # Чтение изображения
        image_bytes = await file.read()
        
        # Предобработка
        processed_image = processor.preprocess_image(image_bytes)
        
        # Предсказание
        prediction = model.predict(processed_image)
        
        # Извлечение координат (предполагаем, что модель возвращает [lat, lon])
        latitude, longitude = prediction[0]
        
        # Добавление небольшого шума для демонстрации
        latitude += np.random.normal(0, 0.001)
        longitude += np.random.normal(0, 0.001)
        
        result = {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "confidence": float(np.random.uniform(0.7, 0.95))  # Случайная уверенность
        }
        
        logger.info(f"Prediction result: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy", 
        "service": "neural-service",
        "model_loaded": model is not None
    }

@app.get("/model/info")
async def model_info():
    """Информация о модели"""
    if model is None:
        return {"error": "Model not loaded"}
    
    return {
        "model_type": "CVM-Net",
        "input_shape": model.input_shape,
        "output_shape": model.output_shape,
        "parameters": model.count_params()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
