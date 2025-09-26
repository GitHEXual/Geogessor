from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import requests
import os
import logging
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.error(f"Error getting address: {e}")
        
        return Address(full_address="Address not found")
    
    def get_street_view_image(self, lat: float, lon: float, heading: int = 0) -> str:
        """Получение Street View изображения"""
        try:
            if not self.google_api_key:
                raise HTTPException(status_code=500, detail="Google API key not configured")
            
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
            logger.error(f"Error getting Street View image: {e}")
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
    logger.info(f"Getting address for coordinates: {coordinates.latitude}, {coordinates.longitude}")
    
    address = service.get_address_from_coordinates(
        coordinates.latitude, 
        coordinates.longitude
    )
    
    logger.info(f"Address found: {address.full_address}")
    return address

@app.post("/get-street-view")
async def get_street_view(coordinates: Coordinates, heading: int = 0):
    """Получение Street View изображения"""
    logger.info(f"Getting Street View for coordinates: {coordinates.latitude}, {coordinates.longitude}")
    
    image_data = service.get_street_view_image(
        coordinates.latitude,
        coordinates.longitude,
        heading
    )
    
    # Конвертация в base64
    import base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    return {
        "image_data": image_base64,
        "metadata": {
            "status": "OK",
            "copyright": "©2023 Google"
        }
    }

@app.post("/calculate-distance")
async def calculate_distance(coord1: Coordinates, coord2: Coordinates):
    """Расчет расстояния между точками"""
    distance = service.calculate_distance(coord1, coord2)
    logger.info(f"Distance calculated: {distance} km")
    return {"distance_km": distance}

@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {
        "status": "healthy",
        "service": "coordinates-service",
        "google_api_configured": bool(service.google_api_key)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
