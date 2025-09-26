from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import httpx
import os
import logging
from typing import Optional
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Geolocation API Gateway",
    description="API Gateway для системы распознавания географических координат",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # В продакшене указать конкретные хосты
)

# Конфигурация сервисов
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
    "image": os.getenv("IMAGE_SERVICE_URL", "http://image-service:8000"),
    "neural": os.getenv("NEURAL_SERVICE_URL", "http://neural-service:8000"),
    "coordinates": os.getenv("COORDINATES_SERVICE_URL", "http://coordinates-service:8000"),
    "export": os.getenv("EXPORT_SERVICE_URL", "http://export-service:8000"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000"),
}

# Rate limiting
request_counts = {}

async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Очистка старых запросов (старше 1 минуты)
    if client_ip in request_counts:
        request_counts[client_ip] = [
            req_time for req_time in request_counts[client_ip]
            if current_time - req_time < 60
        ]
    else:
        request_counts[client_ip] = []
    
    # Проверка лимита (100 запросов в минуту)
    if len(request_counts[client_ip]) >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    request_counts[client_ip].append(current_time)
    
    response = await call_next(request)
    return response

app.middleware("http")(rate_limit_middleware)

async def proxy_request(service_name: str, path: str, method: str, **kwargs):
    """Проксирование запроса к микросервису"""
    service_url = SERVICES.get(service_name)
    if not service_url:
        raise HTTPException(status_code=503, detail=f"Service {service_name} not available")
    
    url = f"{service_url}{path}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, **kwargs)
            return response
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")

# Health check
@app.get("/health")
async def health_check():
    """Проверка состояния API Gateway"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            service: "available" for service in SERVICES.keys()
        }
    }

# Auth routes
@app.post("/auth/login")
async def login(request: Request):
    """Аутентификация пользователя"""
    body = await request.body()
    response = await proxy_request("auth", "/login", "POST", content=body)
    return response.json()

@app.post("/auth/register")
async def register(request: Request):
    """Регистрация пользователя"""
    body = await request.body()
    response = await proxy_request("auth", "/register", "POST", content=body)
    return response.json()

@app.get("/auth/me")
async def get_current_user(request: Request):
    """Получение информации о текущем пользователе"""
    headers = dict(request.headers)
    response = await proxy_request("auth", "/me", "GET", headers=headers)
    return response.json()

# Image processing routes
@app.post("/api/images/upload")
async def upload_images(request: Request):
    """Загрузка и обработка изображений"""
    form_data = await request.form()
    files = await request.form()
    response = await proxy_request("image", "/detect-buildings", "POST", files=files)
    return response.json()

@app.post("/api/images/preprocess")
async def preprocess_image(request: Request):
    """Предобработка изображения"""
    form_data = await request.form()
    files = await request.form()
    response = await proxy_request("image", "/preprocess", "POST", files=files)
    return response.json()

# Neural network routes
@app.post("/api/neural/predict")
async def predict_coordinates(request: Request):
    """Предсказание координат через нейросеть"""
    form_data = await request.form()
    files = await request.form()
    response = await proxy_request("neural", "/predict", "POST", files=files)
    return response.json()

# Coordinates routes
@app.post("/api/coordinates/address")
async def get_address(request: Request):
    """Получение адреса по координатам"""
    body = await request.body()
    response = await proxy_request("coordinates", "/get-address", "POST", content=body)
    return response.json()

@app.post("/api/coordinates/street-view")
async def get_street_view(request: Request):
    """Получение Street View изображения"""
    body = await request.body()
    response = await proxy_request("coordinates", "/get-street-view", "POST", content=body)
    return response.json()

# Export routes
@app.post("/api/export/xlsx")
async def export_xlsx(request: Request):
    """Экспорт данных в XLSX"""
    body = await request.body()
    response = await proxy_request("export", "/export/xlsx", "POST", content=body)
    return response

@app.post("/api/export/images")
async def export_images(request: Request):
    """Экспорт изображений в ZIP"""
    body = await request.body()
    response = await proxy_request("export", "/export/images", "POST", content=body)
    return response

# Notification routes
@app.post("/api/notifications/send")
async def send_notification(request: Request):
    """Отправка уведомления"""
    body = await request.body()
    response = await proxy_request("notification", "/send", "POST", content=body)
    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
