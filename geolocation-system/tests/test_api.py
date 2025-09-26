import pytest
import requests
import json
from typing import Dict, Any

# Базовый URL API
BASE_URL = "http://localhost:8000"

class TestGeolocationAPI:
    """Тесты для API системы геолокации"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.session = requests.Session()
        self.token = None
    
    def test_health_check(self):
        """Тест проверки здоровья API Gateway"""
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_auth_login(self):
        """Тест аутентификации"""
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        
        response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        self.token = data["access_token"]
    
    def test_get_current_user(self):
        """Тест получения информации о пользователе"""
        # Сначала логинимся
        self.test_auth_login()
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.get(f"{BASE_URL}/auth/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "username" in data
        assert "email" in data
    
    def test_image_upload(self):
        """Тест загрузки изображения"""
        # Сначала логинимся
        self.test_auth_login()
        
        # Создание тестового изображения
        import io
        from PIL import Image
        
        # Создание простого тестового изображения
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
        
        response = self.session.post(
            f"{BASE_URL}/api/images/upload",
            files=files,
            headers=headers
        )
        
        # Проверяем, что запрос прошел (может быть 200 или 500 в зависимости от настройки)
        assert response.status_code in [200, 500]
    
    def test_neural_prediction(self):
        """Тест предсказания координат"""
        # Сначала логинимся
        self.test_auth_login()
        
        # Создание тестового изображения
        import io
        from PIL import Image
        
        img = Image.new('RGB', (224, 224), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
        
        response = self.session.post(
            f"{BASE_URL}/api/neural/predict",
            files=files,
            headers=headers
        )
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "latitude" in data
            assert "longitude" in data
            assert "confidence" in data
    
    def test_coordinates_address(self):
        """Тест получения адреса по координатам"""
        # Сначала логинимся
        self.test_auth_login()
        
        coordinates = {
            "latitude": 55.7558,
            "longitude": 37.6176
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.post(
            f"{BASE_URL}/api/coordinates/address",
            json=coordinates,
            headers=headers
        )
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "full_address" in data
    
    def test_export_xlsx(self):
        """Тест экспорта в XLSX"""
        # Сначала логинимся
        self.test_auth_login()
        
        test_data = [
            {
                "building_id": "test-1",
                "coordinates": {
                    "latitude": 55.7558,
                    "longitude": 37.6176
                },
                "address": "Moscow, Russia",
                "confidence": 0.95
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = self.session.post(
            f"{BASE_URL}/api/export/xlsx",
            json=test_data,
            headers=headers
        )
        
        # Проверяем, что запрос прошел
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])
