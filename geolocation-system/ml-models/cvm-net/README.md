# CVM-Net Model

Cross-View Matching Network для распознавания географических координат по фотографиям.

## Описание

CVM-Net - это нейросетевая модель, основанная на архитектуре Siamese network, которая использует VGG16 в качестве backbone и NetVLAD для агрегации признаков. Модель обучена для сопоставления наземных изображений со спутниковыми снимками.

## Архитектура

- **Backbone**: VGG16 (предобученная на ImageNet)
- **Feature Aggregation**: NetVLAD
- **Output**: Координаты (широта, долгота)
- **Input Size**: 224x224x3

## Использование

```python
from cvm_model import CVMModel

# Загрузка модели
model = CVMModel()
model.load_weights('cvm-net-weights.h5')

# Предсказание
coordinates = model.predict(image)
```

## Файлы

- `model.py` - Определение архитектуры модели
- `preprocessing.py` - Функции предобработки
- `training.py` - Скрипт обучения
- `weights/` - Веса модели
- `data/` - Данные для обучения
