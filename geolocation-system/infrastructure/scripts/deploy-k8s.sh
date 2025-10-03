#!/bin/bash

# Скрипт развертывания системы геолокации в Kubernetes

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции для вывода
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

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Проверка зависимостей
check_dependencies() {
    log "🔍 Проверка зависимостей..."
    
    if ! command -v kubectl &> /dev/null; then
        error "kubectl не установлен"
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен"
    fi
    
    if ! command -v helm &> /dev/null; then
        warn "Helm не установлен, пропускаем установку через Helm"
    fi
    
    log "✅ Все зависимости проверены"
}

# Проверка кластера
check_cluster() {
    log "🔍 Проверка кластера Kubernetes..."
    
    if ! kubectl cluster-info &> /dev/null; then
        error "Не удается подключиться к кластеру Kubernetes"
    fi
    
    local nodes=$(kubectl get nodes --no-headers | wc -l)
    log "✅ Кластер доступен, узлов: $nodes"
}

# Сборка Docker образов
build_images() {
    log "🔨 Сборка Docker образов..."
    
    # Проверка, что мы в правильной директории
    if [ ! -f "docker-compose.yml" ]; then
        error "Запустите скрипт из корневой директории проекта"
    fi
    
    # Frontend
    log "📦 Сборка frontend..."
    docker build -t geolocation/frontend:latest ./frontend/
    
    # Backend services
    for service in api-gateway auth-service image-service coordinates-service export-service notification-service; do
        log "📦 Сборка $service..."
        docker build -t geolocation/$service:latest ./backend/$service/
    done
    
    log "✅ Все образы собраны успешно!"
}

# Создание namespace
create_namespace() {
    log "📦 Создание namespace..."
    
    kubectl create namespace geolocation-system --dry-run=client -o yaml | kubectl apply -f -
    log "✅ Namespace создан"
}

# Создание секретов
create_secrets() {
    log "🔐 Создание секретов..."
    
    # PostgreSQL secret
    kubectl create secret generic postgres-secret \
        --from-literal=password=your-secure-password \
        --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -
    
    # JWT secret
    kubectl create secret generic jwt-secret \
        --from-literal=secret-key=your-jwt-secret-key \
        --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -
    
    # Google API secret
    kubectl create secret generic google-api-secret \
        --from-literal=api-key=your-google-api-key \
        --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -
    
    # MinIO secret
    kubectl create secret generic minio-secret \
        --from-literal=access-key=minioadmin \
        --from-literal=secret-key=minioadmin \
        --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -
    
    log "✅ Секреты созданы"
}

# Создание ConfigMap
create_configmap() {
    log "⚙️ Создание ConfigMap..."
    
    kubectl create configmap app-config \
        --from-literal=database-url=postgresql://postgres:password@postgres-service:5432/geolocation_db \
        --from-literal=redis-url=redis://redis-service:6379 \
        --from-literal=minio-endpoint=minio-service:9000 \
        --from-literal=auth-service-url=http://auth-service:8000 \
        --from-literal=image-service-url=http://image-service:8000 \
        --from-literal=neural-service-url=http://neural-service:8000 \
        --from-literal=coordinates-service-url=http://coordinates-service:8000 \
        --from-literal=export-service-url=http://export-service:8000 \
        --from-literal=notification-service-url=http://notification-service:8000 \
        --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -
    
    log "✅ ConfigMap создан"
}

# Применение PersistentVolumes
apply_persistent_volumes() {
    log "💾 Применение PersistentVolumes..."
    
    kubectl apply -f infrastructure/kubernetes/persistent-volumes.yaml
    log "✅ PersistentVolumes применены"
}

# Развертывание базы данных
deploy_databases() {
    log "🗄️ Развертывание базы данных..."
    
    # PostgreSQL
    kubectl apply -f infrastructure/kubernetes/postgres.yaml
    log "✅ PostgreSQL развернут"
    
    # Redis
    kubectl apply -f infrastructure/kubernetes/redis.yaml
    log "✅ Redis развернут"
    
    # MinIO
    kubectl apply -f infrastructure/kubernetes/minio.yaml
    log "✅ MinIO развернут"
}

# Ожидание готовности баз данных
wait_for_databases() {
    log "⏳ Ожидание готовности баз данных..."
    
    # PostgreSQL
    kubectl wait --for=condition=ready pod -l app=postgres -n geolocation-system --timeout=300s
    log "✅ PostgreSQL готов"
    
    # Redis
    kubectl wait --for=condition=ready pod -l app=redis -n geolocation-system --timeout=300s
    log "✅ Redis готов"
    
    # MinIO
    kubectl wait --for=condition=ready pod -l app=minio -n geolocation-system --timeout=300s
    log "✅ MinIO готов"
}

# Развертывание микросервисов
deploy_services() {
    log "🚀 Развертывание микросервисов..."
    
    # Auth Service
    kubectl apply -f infrastructure/kubernetes/auth-service.yaml
    log "✅ Auth Service развернут"
    
    # Neural Service (закомментирован)
    # kubectl apply -f infrastructure/kubernetes/neural-service.yaml
    # log "✅ Neural Service развернут"
    
    # Image Service
    kubectl apply -f infrastructure/kubernetes/image-service.yaml
    log "✅ Image Service развернут"
    
    # Coordinates Service
    kubectl apply -f infrastructure/kubernetes/coordinates-service.yaml
    log "✅ Coordinates Service развернут"
    
    # Export Service
    kubectl apply -f infrastructure/kubernetes/export-service.yaml
    log "✅ Export Service развернут"
    
    # Notification Service
    kubectl apply -f infrastructure/kubernetes/notification-service.yaml
    log "✅ Notification Service развернут"
    
    # API Gateway
    kubectl apply -f infrastructure/kubernetes/api-gateway.yaml
    log "✅ API Gateway развернут"
    
    # Frontend
    kubectl apply -f infrastructure/kubernetes/frontend.yaml
    log "✅ Frontend развернут"
}

# Настройка Ingress
setup_ingress() {
    log "🌐 Настройка Ingress..."
    
    # Проверка наличия NGINX Ingress Controller
    if kubectl get pods -n ingress-nginx &> /dev/null; then
        log "✅ NGINX Ingress Controller уже установлен"
    else
        warn "NGINX Ingress Controller не найден, устанавливаем..."
        
        if command -v helm &> /dev/null; then
            helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
            helm repo update
            helm install ingress-nginx ingress-nginx/ingress-nginx \
                --namespace ingress-nginx \
                --create-namespace \
                --set controller.service.type=LoadBalancer
        else
            warn "Helm не установлен, пропускаем установку Ingress Controller"
        fi
    fi
    
    # Применение Ingress
    kubectl apply -f infrastructure/kubernetes/ingress.yaml
    log "✅ Ingress настроен"
}

# Настройка мониторинга
setup_monitoring() {
    log "📊 Настройка мониторинга..."
    
    if command -v helm &> /dev/null; then
        # Prometheus
        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
        helm repo update
        
        if ! helm list -n monitoring &> /dev/null; then
            helm install prometheus prometheus-community/kube-prometheus-stack \
                --namespace monitoring \
                --create-namespace \
                --set grafana.adminPassword=admin
            log "✅ Prometheus и Grafana установлены"
        else
            log "✅ Prometheus уже установлен"
        fi
    else
        warn "Helm не установлен, пропускаем установку мониторинга"
    fi
}

# Настройка HPA
setup_hpa() {
    log "📈 Настройка HPA..."
    
    kubectl apply -f infrastructure/kubernetes/hpa.yaml
    log "✅ HPA настроен"
}

# Проверка статуса
check_status() {
    log "🔍 Проверка статуса развертывания..."
    
    # Проверка подов
    kubectl get pods -n geolocation-system
    
    # Проверка сервисов
    kubectl get services -n geolocation-system
    
    # Проверка Ingress
    kubectl get ingress -n geolocation-system
    
    # Проверка HPA
    kubectl get hpa -n geolocation-system
    
    log "✅ Статус проверен"
}

# Настройка DNS для Minikube
setup_dns() {
    if kubectl config current-context | grep -q minikube; then
        log "🌐 Настройка DNS для Minikube..."
        
        local minikube_ip=$(minikube ip)
        local hosts_entry="$minikube_ip geolocation.local api.geolocation.local"
        
        # Проверка операционной системы
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            # Windows
            echo "$hosts_entry" >> C:\\Windows\\System32\\drivers\\etc\\hosts
        else
            # Linux/macOS
            echo "$hosts_entry" | sudo tee -a /etc/hosts
        fi
        
        log "✅ DNS настроен: $hosts_entry"
    fi
}

# Вывод информации о доступе
show_access_info() {
    log "🎉 Развертывание завершено!"
    echo ""
    info "📋 Информация о доступе:"
    echo ""
    echo "🌐 Frontend: http://geolocation.local"
    echo "🔗 API: http://api.geolocation.local"
    echo "📊 Grafana: http://localhost:3000 (admin/admin)"
    echo ""
    info "🔧 Полезные команды:"
    echo ""
    echo "kubectl get pods -n geolocation-system"
    echo "kubectl logs -f deployment/api-gateway -n geolocation-system"
    echo "kubectl port-forward service/frontend 3000:3000 -n geolocation-system"
    echo "kubectl port-forward service/api-gateway 8000:8000 -n geolocation-system"
    echo ""
    info "🧹 Очистка ресурсов:"
    echo ""
    echo "kubectl delete namespace geolocation-system"
    echo ""
}

# Очистка ресурсов
cleanup() {
    log "🧹 Очистка ресурсов..."
    
    kubectl delete namespace geolocation-system
    log "✅ Ресурсы очищены"
}

# Основная функция
main() {
    case "${1:-deploy}" in
        "deploy")
            check_dependencies
            check_cluster
            build_images
            create_namespace
            create_secrets
            create_configmap
            apply_persistent_volumes
            deploy_databases
            wait_for_databases
            deploy_services
            setup_ingress
            setup_monitoring
            setup_hpa
            setup_dns
            check_status
            show_access_info
            ;;
        "cleanup")
            cleanup
            ;;
        "status")
            check_status
            ;;
        "build")
            build_images
            ;;
        *)
            echo "Использование: $0 {deploy|cleanup|status|build}"
            echo ""
            echo "Команды:"
            echo "  deploy   - Полное развертывание системы"
            echo "  cleanup  - Удаление всех ресурсов"
            echo "  status   - Проверка статуса"
            echo "  build    - Только сборка образов"
            exit 1
            ;;
    esac
}

# Запуск
main "$@"
