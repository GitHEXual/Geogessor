import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import logging
from model import CVMModel
from preprocessing import ImagePreprocessor, create_tf_dataset
import json
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CVMTrainer:
    def __init__(self, model: CVMModel, config: dict):
        self.model = model
        self.config = config
        self.history = None
    
    def prepare_data(self, data_dir: str):
        """Подготовка данных для обучения"""
        logger.info("Preparing data for training...")
        
        # Загрузка путей к изображениям и координат
        image_paths = []
        coordinates = []
        
        # Предполагаем, что данные хранятся в формате:
        # data_dir/
        #   images/
        #     image1.jpg
        #     image2.jpg
        #   coordinates.json
        
        images_dir = os.path.join(data_dir, "images")
        coords_file = os.path.join(data_dir, "coordinates.json")
        
        if not os.path.exists(images_dir):
            raise ValueError(f"Images directory not found: {images_dir}")
        
        if not os.path.exists(coords_file):
            raise ValueError(f"Coordinates file not found: {coords_file}")
        
        # Загрузка координат
        with open(coords_file, 'r') as f:
            coords_data = json.load(f)
        
        # Подготовка данных
        for item in coords_data:
            image_path = os.path.join(images_dir, item['filename'])
            if os.path.exists(image_path):
                image_paths.append(image_path)
                coordinates.append([item['latitude'], item['longitude']])
        
        logger.info(f"Loaded {len(image_paths)} images for training")
        return image_paths, coordinates
    
    def split_data(self, image_paths: list, coordinates: list, 
                   train_ratio: float = 0.8, val_ratio: float = 0.1):
        """Разделение данных на train/val/test"""
        num_samples = len(image_paths)
        train_size = int(num_samples * train_ratio)
        val_size = int(num_samples * val_ratio)
        
        # Перемешивание данных
        indices = np.random.permutation(num_samples)
        
        train_indices = indices[:train_size]
        val_indices = indices[train_size:train_size + val_size]
        test_indices = indices[train_size + val_size:]
        
        # Разделение данных
        train_data = {
            'images': [image_paths[i] for i in train_indices],
            'coordinates': [coordinates[i] for i in train_indices]
        }
        
        val_data = {
            'images': [image_paths[i] for i in val_indices],
            'coordinates': [coordinates[i] for i in val_indices]
        }
        
        test_data = {
            'images': [image_paths[i] for i in test_indices],
            'coordinates': [coordinates[i] for i in test_indices]
        }
        
        logger.info(f"Data split - Train: {len(train_data['images'])}, "
                   f"Val: {len(val_data['images'])}, Test: {len(test_data['images'])}")
        
        return train_data, val_data, test_data
    
    def create_datasets(self, train_data: dict, val_data: dict, test_data: dict):
        """Создание TensorFlow datasets"""
        train_dataset = create_tf_dataset(
            train_data['images'], 
            train_data['coordinates'],
            batch_size=self.config['batch_size']
        )
        
        val_dataset = create_tf_dataset(
            val_data['images'], 
            val_data['coordinates'],
            batch_size=self.config['batch_size']
        )
        
        test_dataset = create_tf_dataset(
            test_data['images'], 
            test_data['coordinates'],
            batch_size=self.config['batch_size']
        )
        
        return train_dataset, val_dataset, test_dataset
    
    def setup_callbacks(self, save_dir: str):
        """Настройка callbacks для обучения"""
        callbacks = [
            ModelCheckpoint(
                filepath=os.path.join(save_dir, 'best_model.h5'),
                monitor='val_loss',
                save_best_only=True,
                save_weights_only=True,
                verbose=1
            ),
            EarlyStopping(
                monitor='val_loss',
                patience=self.config['patience'],
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            )
        ]
        
        return callbacks
    
    def train(self, train_dataset, val_dataset, save_dir: str):
        """Обучение модели"""
        logger.info("Starting model training...")
        
        # Настройка callbacks
        callbacks = self.setup_callbacks(save_dir)
        
        # Обучение
        self.history = self.model.model.fit(
            train_dataset,
            validation_data=val_dataset,
            epochs=self.config['epochs'],
            callbacks=callbacks,
            verbose=1
        )
        
        # Сохранение истории обучения
        history_path = os.path.join(save_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history.history, f, indent=2)
        
        logger.info("Training completed successfully")
        return self.history
    
    def evaluate(self, test_dataset):
        """Оценка модели на тестовых данных"""
        logger.info("Evaluating model on test data...")
        
        results = self.model.model.evaluate(test_dataset, verbose=1)
        
        logger.info(f"Test results - Loss: {results[0]:.4f}, MAE: {results[1]:.4f}, MSE: {results[2]:.4f}")
        return results
    
    def save_model(self, save_dir: str):
        """Сохранение модели"""
        model_path = os.path.join(save_dir, 'cvm_model.h5')
        self.model.model.save(model_path)
        logger.info(f"Model saved to {model_path}")
        
        # Сохранение конфигурации
        config_path = os.path.join(save_dir, 'model_config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        logger.info(f"Configuration saved to {config_path}")

def main():
    """Основная функция обучения"""
    # Конфигурация обучения
    config = {
        'batch_size': 32,
        'epochs': 100,
        'learning_rate': 0.001,
        'patience': 15,
        'data_dir': 'data',
        'save_dir': 'models'
    }
    
    # Создание директорий
    os.makedirs(config['save_dir'], exist_ok=True)
    
    # Создание модели
    model = CVMModel()
    model.compile_model(learning_rate=config['learning_rate'])
    
    # Создание тренера
    trainer = CVMTrainer(model, config)
    
    try:
        # Подготовка данных
        image_paths, coordinates = trainer.prepare_data(config['data_dir'])
        
        # Разделение данных
        train_data, val_data, test_data = trainer.split_data(image_paths, coordinates)
        
        # Создание datasets
        train_dataset, val_dataset, test_dataset = trainer.create_datasets(
            train_data, val_data, test_data
        )
        
        # Обучение
        history = trainer.train(train_dataset, val_dataset, config['save_dir'])
        
        # Оценка
        test_results = trainer.evaluate(test_dataset)
        
        # Сохранение модели
        trainer.save_model(config['save_dir'])
        
        logger.info("Training pipeline completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    main()
