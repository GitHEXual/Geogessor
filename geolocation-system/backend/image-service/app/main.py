from fastapi import FastAPI, File, UploadFile, HTTPException
import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import List, Dict
import logging
import os
from minio import Minio
from minio.error import S3Error

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Image Processing Service")

# Настройка MinIO
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

# Инициализация MinIO клиента
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Создание bucket если не существует
try:
    if not minio_client.bucket_exists("images"):
        minio_client.make_bucket("images")
        logger.info("Created 'images' bucket")
except S3Error as e:
    logger.error(f"Error creating bucket: {e}")

class BuildingDetector:
    def __init__(self):
        # Загрузка модели для детекции зданий (YOLO, R-CNN и т.д.)
        # Для демонстрации используем простой алгоритм
        pass
    
    def detect_buildings(self, image: np.ndarray) -> List[Dict]:
        """Детекция зданий на изображении"""
        # Здесь должна быть реализация детекции зданий
        # Для демонстрации возвращаем заглушку
        buildings = []
        
        # Простая детекция на основе контуров
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Фильтрация контуров по размеру
        height, width = image.shape[:2]
        min_area = (width * height) * 0.01  # Минимальная площадь 1% от изображения
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(contour)
                buildings.append({
                    "bbox": [x, y, x + w, y + h],
                    "confidence": min(0.95, area / (width * height) * 10),
                    "class": "building"
                })
        
        # Если не найдено зданий, добавляем заглушку
        if not buildings:
            buildings.append({
                "bbox": [0.1 * width, 0.1 * height, 0.8 * width, 0.8 * height],
                "confidence": 0.85,
                "class": "building"
            })
        
        return buildings[:5]  # Максимум 5 зданий
    
    def crop_building(self, image: np.ndarray, bbox: List[int]) -> np.ndarray:
        """Обрезка здания по bbox"""
        x1, y1, x2, y2 = bbox
        return image[y1:y2, x1:x2]

detector = BuildingDetector()

async def save_image_to_storage(image_bytes: bytes, filename: str) -> str:
    """Сохранение изображения в MinIO"""
    try:
        minio_client.put_object(
            "images",
            filename,
            io.BytesIO(image_bytes),
            length=len(image_bytes),
            content_type="image/jpeg"
        )
        logger.info(f"Image saved to storage: {filename}")
        return filename
    except S3Error as e:
        logger.error(f"Error saving image: {e}")
        raise HTTPException(status_code=500, detail="Failed to save image")

@app.post("/detect-buildings")
async def detect_buildings(file: UploadFile = File(...)):
    """Детекция зданий на изображении"""
    try:
        logger.info(f"Processing image: {file.filename}")
        
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
            
            # Сохранение обрезанного изображения
            filename = f"building_{i}_{file.filename}"
            await save_image_to_storage(buffer.tobytes(), filename)
            
            cropped_buildings.append({
                "id": i,
                "bbox": building["bbox"],
                "confidence": building["confidence"],
                "cropped_image": cropped_base64,
                "filename": filename
            })
        
        logger.info(f"Detected {len(buildings)} buildings")
        return {
            "buildings": cropped_buildings,
            "total_detected": len(buildings)
        }
    
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/preprocess")
async def preprocess_image(file: UploadFile = File(...)):
    """Предобработка изображения для нейросети"""
    try:
        logger.info(f"Preprocessing image: {file.filename}")
        
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
        
        logger.info("Image preprocessed successfully")
        return {"processed_image": processed_base64}
    
    except Exception as e:
        logger.error(f"Error preprocessing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    try:
        # Проверка подключения к MinIO
        minio_client.bucket_exists("images")
        return {
            "status": "healthy",
            "service": "image-service",
            "storage": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "image-service",
            "storage": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
