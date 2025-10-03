# Neural Service - Информация

## Статус

🚫 **Neural Service временно отключен**

## Причина

Neural Service требует настройки и интеграции с CVM-Net моделью, что включает:

1. Загрузку предобученной модели CVM-Net
2. Настройку TensorFlow/PyTorch окружения
3. Конфигурацию GPU (опционально)
4. Тестирование и валидацию модели

## Что было изменено

### Docker Compose
- Сервис `neural-service` закомментирован в `docker-compose.yml`

### API Gateway
- Маршрут `/api/neural/predict` закомментирован
- Ссылка на `neural-service` удалена из конфигурации

### Kubernetes
- Манифест `neural-service.yaml` закомментирован
- Удалены ссылки из ConfigMap и других сервисов

### Документация
- Обновлена API документация с пометкой о недоступности
- Обновлены README файлы

## Включение Neural Service

Для включения Neural Service выполните следующие шаги:

### 1. Подготовка модели
```bash
# Скачайте предобученную CVM-Net модель
mkdir -p ml-models/cvm-net
# Разместите файлы модели в ml-models/cvm-net/
```

### 2. Восстановление кода
```bash
# Восстановите файлы neural-service из git истории или создайте заново
git checkout HEAD~1 -- backend/neural-service/
```

### 3. Настройка окружения
```bash
# Добавьте переменные окружения
export MODEL_PATH=/app/models/cvm-net
export GPU_ENABLED=true  # если используете GPU
```

### 4. Сборка и развертывание
```bash
# Раскомментируйте сервис в docker-compose.yml
# Раскомментируйте маршруты в API Gateway
# Раскомментируйте манифесты в Kubernetes
# Пересоберите и разверните систему
```

## Альтернативы

Пока Neural Service не настроен, можно использовать:

1. **Заглушки координат** - возвращать случайные координаты для тестирования
2. **Внешние API** - интеграция с Google Vision API или другими сервисами
3. **Простая логика** - базовое определение координат на основе метаданных изображения

## Файлы для восстановления

Следующие файлы содержат закомментированный код Neural Service:

- `docker-compose.yml`
- `backend/api-gateway/app/main.py`
- `infrastructure/kubernetes/neural-service.yaml`
- `infrastructure/kubernetes/configmap.yaml`
- `infrastructure/kubernetes/api-gateway.yaml`
- `infrastructure/scripts/deploy-k8s.sh`

## Поддержка

При возникновении вопросов по настройке Neural Service:

1. Изучите документацию CVM-Net
2. Проверьте совместимость версий TensorFlow
3. Убедитесь в корректности путей к модели
4. Проверьте логи контейнера при запуске
