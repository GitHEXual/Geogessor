import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from typing import Tuple, List
import logging

logger = logging.getLogger(__name__)

class ImagePreprocessor:
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Предобработка изображения для CVM-Net"""
        try:
            # Загрузка изображения
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image from {image_path}")
            
            # Конвертация BGR -> RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Изменение размера
            image = cv2.resize(image, self.target_size)
            
            # Нормализация
            image = image.astype(np.float32) / 255.0
            
            return image
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            raise
    
    def preprocess_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """Предобработка изображения из байтов"""
        try:
            # Загрузка изображения из байтов
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Could not decode image from bytes")
            
            # Конвертация BGR -> RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Изменение размера
            image = cv2.resize(image, self.target_size)
            
            # Нормализация
            image = image.astype(np.float32) / 255.0
            
            return image
        except Exception as e:
            logger.error(f"Error preprocessing image from bytes: {e}")
            raise
    
    def augment_image(self, image: np.ndarray) -> List[np.ndarray]:
        """Аугментация изображения"""
        augmented_images = [image]
        
        # Горизонтальное отражение
        flipped = cv2.flip(image, 1)
        augmented_images.append(flipped)
        
        # Поворот на 90 градусов
        rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        augmented_images.append(rotated)
        
        # Поворот на 180 градусов
        rotated180 = cv2.rotate(image, cv2.ROTATE_180)
        augmented_images.append(rotated180)
        
        return augmented_images
    
    def normalize_coordinates(self, lat: float, lon: float) -> Tuple[float, float]:
        """Нормализация координат для обучения"""
        # Нормализация к диапазону [-1, 1]
        norm_lat = (lat - 90.0) / 90.0
        norm_lon = (lon - 180.0) / 180.0
        return norm_lat, norm_lon
    
    def denormalize_coordinates(self, norm_lat: float, norm_lon: float) -> Tuple[float, float]:
        """Денормализация координат"""
        lat = norm_lat * 90.0 + 90.0
        lon = norm_lon * 180.0 + 180.0
        return lat, lon

class DataGenerator:
    def __init__(self, image_paths: List[str], coordinates: List[Tuple[float, float]], 
                 batch_size: int = 32, preprocessor: ImagePreprocessor = None):
        self.image_paths = image_paths
        self.coordinates = coordinates
        self.batch_size = batch_size
        self.preprocessor = preprocessor or ImagePreprocessor()
        self.num_samples = len(image_paths)
    
    def __len__(self):
        return int(np.ceil(self.num_samples / self.batch_size))
    
    def __getitem__(self, idx):
        """Получение батча данных"""
        start_idx = idx * self.batch_size
        end_idx = min(start_idx + self.batch_size, self.num_samples)
        
        batch_images = []
        batch_coordinates = []
        
        for i in range(start_idx, end_idx):
            try:
                # Предобработка изображения
                image = self.preprocessor.preprocess_image(self.image_paths[i])
                batch_images.append(image)
                
                # Нормализация координат
                lat, lon = self.coordinates[i]
                norm_lat, norm_lon = self.preprocessor.normalize_coordinates(lat, lon)
                batch_coordinates.append([norm_lat, norm_lon])
                
            except Exception as e:
                logger.warning(f"Error processing image {i}: {e}")
                continue
        
        return np.array(batch_images), np.array(batch_coordinates)
    
    def get_augmented_data(self, augmentation_factor: int = 4):
        """Получение аугментированных данных"""
        augmented_images = []
        augmented_coordinates = []
        
        for i in range(len(self.image_paths)):
            try:
                image = self.preprocessor.preprocess_image(self.image_paths[i])
                augmented = self.preprocessor.augment_image(image)
                
                for aug_image in augmented[:augmentation_factor]:
                    augmented_images.append(aug_image)
                    augmented_coordinates.append(self.coordinates[i])
                    
            except Exception as e:
                logger.warning(f"Error augmenting image {i}: {e}")
                continue
        
        return augmented_images, augmented_coordinates

def create_tf_dataset(image_paths: List[str], coordinates: List[Tuple[float, float]], 
                     batch_size: int = 32) -> tf.data.Dataset:
    """Создание TensorFlow Dataset"""
    def load_and_preprocess(image_path, lat, lon):
        # Загрузка и предобработка изображения
        image = tf.io.read_file(image_path)
        image = tf.image.decode_jpeg(image, channels=3)
        image = tf.image.resize(image, [224, 224])
        image = tf.cast(image, tf.float32) / 255.0
        
        # Нормализация координат
        norm_lat = (lat - 90.0) / 90.0
        norm_lon = (lon - 180.0) / 180.0
        
        return image, [norm_lat, norm_lon]
    
    dataset = tf.data.Dataset.from_tensor_slices((image_paths, coordinates))
    dataset = dataset.map(load_and_preprocess, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset

if __name__ == "__main__":
    # Тестирование предобработки
    preprocessor = ImagePreprocessor()
    
    # Тестовые координаты
    lat, lon = 55.7558, 37.6176  # Москва
    norm_lat, norm_lon = preprocessor.normalize_coordinates(lat, lon)
    print(f"Original: ({lat}, {lon})")
    print(f"Normalized: ({norm_lat}, {norm_lon})")
    
    # Обратная нормализация
    denorm_lat, denorm_lon = preprocessor.denormalize_coordinates(norm_lat, norm_lon)
    print(f"Denormalized: ({denorm_lat}, {denorm_lon})")
