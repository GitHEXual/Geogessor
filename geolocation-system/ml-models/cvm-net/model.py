import tensorflow as tf
import numpy as np
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import logging

logger = logging.getLogger(__name__)

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
        x = Dense(512, activation='relu', name='fc1')(x)
        x = Dropout(0.5)(x)
        x = Dense(256, activation='relu', name='fc2')(x)
        x = Dropout(0.3)(x)
        coordinates = Dense(2, activation='linear', name='coordinates')(x)
        
        # Создание модели
        model = Model(inputs=base_model.input, outputs=coordinates)
        
        return model
    
    def compile_model(self, learning_rate=0.001):
        """Компиляция модели"""
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='mse',
            metrics=['mae', 'mse']
        )
        logger.info("Model compiled successfully")
    
    def load_weights(self, weights_path):
        """Загрузка весов модели"""
        try:
            self.model.load_weights(weights_path)
            logger.info(f"Model weights loaded from {weights_path}")
        except Exception as e:
            logger.error(f"Failed to load weights: {e}")
            raise
    
    def save_weights(self, weights_path):
        """Сохранение весов модели"""
        try:
            self.model.save_weights(weights_path)
            logger.info(f"Model weights saved to {weights_path}")
        except Exception as e:
            logger.error(f"Failed to save weights: {e}")
            raise
    
    def predict(self, image):
        """Предсказание координат"""
        if len(image.shape) == 3:
            image = np.expand_dims(image, axis=0)
        
        prediction = self.model.predict(image)
        return prediction
    
    def train(self, train_data, val_data, epochs=100, batch_size=32):
        """Обучение модели"""
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7
            )
        ]
        
        history = self.model.fit(
            train_data,
            validation_data=val_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def get_model_summary(self):
        """Получение информации о модели"""
        return self.model.summary()
    
    def freeze_base_layers(self):
        """Заморозка базовых слоев VGG16"""
        for layer in self.model.layers[:-4]:  # Замораживаем все кроме последних 4 слоев
            layer.trainable = False
        logger.info("Base layers frozen")
    
    def unfreeze_base_layers(self):
        """Разморозка базовых слоев для fine-tuning"""
        for layer in self.model.layers:
            layer.trainable = True
        logger.info("Base layers unfrozen for fine-tuning")

class NetVLAD:
    """NetVLAD слой для агрегации признаков"""
    def __init__(self, num_clusters=64, feature_dim=512):
        self.num_clusters = num_clusters
        self.feature_dim = feature_dim
    
    def __call__(self, features):
        """Применение NetVLAD к признакам"""
        # Упрощенная реализация NetVLAD
        # В реальной реализации здесь была бы более сложная логика
        return tf.reduce_mean(features, axis=1)

def create_cvm_model(input_shape=(224, 224, 3)):
    """Фабричная функция для создания CVM модели"""
    model = CVMModel(input_shape)
    model.compile_model()
    return model

if __name__ == "__main__":
    # Создание и тестирование модели
    model = create_cvm_model()
    model.get_model_summary()
    
    # Тестовое предсказание
    test_image = np.random.random((1, 224, 224, 3))
    prediction = model.predict(test_image)
    print(f"Test prediction: {prediction}")
