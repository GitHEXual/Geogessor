from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import redis
import json
import logging
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service")

# Настройка Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis_client = redis.from_url(REDIS_URL)

class Notification(BaseModel):
    user_id: int
    title: str
    message: str
    type: str = "info"  # info, success, warning, error
    timestamp: Optional[datetime] = None

class NotificationService:
    def __init__(self):
        self.redis_client = redis_client
    
    def send_notification(self, notification: Notification) -> bool:
        """Отправка уведомления пользователю"""
        try:
            notification.timestamp = datetime.utcnow()
            
            # Сохранение уведомления в Redis
            key = f"notifications:{notification.user_id}"
            notification_data = notification.dict()
            notification_data['timestamp'] = notification.timestamp.isoformat()
            
            self.redis_client.lpush(key, json.dumps(notification_data))
            self.redis_client.expire(key, 86400 * 7)  # Хранение 7 дней
            
            logger.info(f"Notification sent to user {notification.user_id}: {notification.title}")
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Получение уведомлений пользователя"""
        try:
            key = f"notifications:{user_id}"
            notifications = self.redis_client.lrange(key, 0, limit - 1)
            
            result = []
            for notification_json in notifications:
                notification_data = json.loads(notification_json)
                result.append(notification_data)
            
            logger.info(f"Retrieved {len(result)} notifications for user {user_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    def mark_notification_read(self, user_id: int, notification_id: str) -> bool:
        """Отметка уведомления как прочитанного"""
        try:
            # В реальной системе здесь была бы более сложная логика
            logger.info(f"Notification {notification_id} marked as read for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

service = NotificationService()

@app.post("/send")
async def send_notification(notification: Notification):
    """Отправка уведомления"""
    try:
        success = service.send_notification(notification)
        if success:
            return {"message": "Notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification")
    except Exception as e:
        logger.error(f"Error in send notification endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user/{user_id}")
async def get_user_notifications(user_id: int, limit: int = 50):
    """Получение уведомлений пользователя"""
    try:
        notifications = service.get_user_notifications(user_id, limit)
        return {"notifications": notifications}
    except Exception as e:
        logger.error(f"Error in get notifications endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mark-read/{user_id}/{notification_id}")
async def mark_notification_read(user_id: int, notification_id: str):
    """Отметка уведомления как прочитанного"""
    try:
        success = service.mark_notification_read(user_id, notification_id)
        if success:
            return {"message": "Notification marked as read"}
        else:
            raise HTTPException(status_code=500, detail="Failed to mark notification as read")
    except Exception as e:
        logger.error(f"Error in mark read endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    try:
        # Проверка подключения к Redis
        redis_client.ping()
        return {
            "status": "healthy",
            "service": "notification-service",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "notification-service",
            "redis": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
