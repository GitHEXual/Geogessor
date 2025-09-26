#!/bin/bash

# Скрипт развертывания системы геолокации

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Проверка зависимостей
check_dependencies() {
    log "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен"
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен"
    fi
    
    if ! command -v kubectl &> /dev/null; then
        warn "kubectl не установлен, пропускаем Kubernetes развертывание"
    fi
    
    log "Все зависимости проверены"
}

# Сборка Docker образов
build_images() {
    log "Сборка Docker образов..."
    
    # Frontend
    log "Сборка frontend..."
    docker build -t geolocation/frontend:latest ./frontend/
    
    # Backend services
    for service in api-gateway auth-service neural-service image-service coordinates-service export-service notification-service; do
        log "Сборка $service..."
        docker build -t geolocation/$service:latest ./backend/$service/
    done
    
    log "Все образы собраны"
}

# Развертывание с Docker Compose
deploy_docker_compose() {
    log "Развертывание с Docker Compose..."
    
    # Создание .env файла если не существует
    if [ ! -f .env ]; then
        log "Создание .env файла..."
        cat > .env << EOF
# Database
POSTGRES_DB=geolocation_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis
REDIS_URL=redis://redis:6379

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# Google API
GOOGLE_API_KEY=your-google-api-key-here

# JWT Secret
SECRET_KEY=your-secret-key-here
EOF
        warn "Пожалуйста, обновите .env файл с вашими API ключами"
    fi
    
    # Запуск сервисов
    docker-compose up -d
    
    log "Сервисы запущены с Docker Compose"
}

# Развертывание в Kubernetes
deploy_kubernetes() {
    log "Развертывание в Kubernetes..."
    
    # Применение манифестов
    kubectl apply -f infrastructure/kubernetes/namespace.yaml
    kubectl apply -f infrastructure/kubernetes/postgres.yaml
    kubectl apply -f infrastructure/kubernetes/redis.yaml
    kubectl apply -f infrastructure/kubernetes/neural-service.yaml
    kubectl apply -f infrastructure/kubernetes/api-gateway.yaml
    
    log "Kubernetes развертывание завершено"
}

# Проверка состояния сервисов
check_services() {
    log "Проверка состояния сервисов..."
    
    # Проверка Docker Compose сервисов
    if docker-compose ps | grep -q "Up"; then
        log "Docker Compose сервисы работают"
    else
        warn "Некоторые Docker Compose сервисы не работают"
    fi
    
    # Проверка Kubernetes подов
    if command -v kubectl &> /dev/null; then
        if kubectl get pods -n geolocation-system | grep -q "Running"; then
            log "Kubernetes поды работают"
        else
            warn "Некоторые Kubernetes поды не работают"
        fi
    fi
}

# Очистка
cleanup() {
    log "Очистка ресурсов..."
    
    # Остановка Docker Compose
    docker-compose down
    
    # Удаление Kubernetes ресурсов
    if command -v kubectl &> /dev/null; then
        kubectl delete namespace geolocation-system
    fi
    
    log "Очистка завершена"
}

# Основная функция
main() {
    case "${1:-deploy}" in
        "deploy")
            check_dependencies
            build_images
            deploy_docker_compose
            if command -v kubectl &> /dev/null; then
                deploy_kubernetes
            fi
            check_services
            log "Развертывание завершено!"
            ;;
        "cleanup")
            cleanup
            ;;
        "check")
            check_services
            ;;
        *)
            echo "Использование: $0 {deploy|cleanup|check}"
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
