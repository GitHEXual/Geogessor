# Полное руководство по развертыванию в Kubernetes

## Содержание
1. [Предварительные требования](#предварительные-требования)
2. [Подготовка кластера](#подготовка-кластера)
3. [Сборка Docker образов](#сборка-docker-образов)
4. [Настройка секретов и конфигураций](#настройка-секретов-и-конфигураций)
5. [Развертывание базы данных](#развертывание-базы-данных)
6. [Развертывание микросервисов](#развертывание-микросервисов)
7. [Настройка Ingress](#настройка-ingress)
8. [Мониторинг и логирование](#мониторинг-и-логирование)
9. [Масштабирование](#масштабирование)
10. [Устранение неполадок](#устранение-неполадок)

## Предварительные требования

### 1. Установка необходимых инструментов

#### kubectl
```bash
# Windows (PowerShell)
curl -LO "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe"
Move-Item kubectl.exe C:\Windows\System32\

# Linux
curl -LO "https://dl.k8s.io/release/v1.28.0/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS
curl -LO "https://dl.k8s.io/release/v1.28.0/bin/darwin/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

#### Helm
```bash
# Windows (PowerShell)
choco install kubernetes-helm

# Linux/macOS
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Docker Desktop с Kubernetes
1. Установите Docker Desktop
2. Включите Kubernetes в настройках
3. Или используйте Minikube/kind для локального кластера

### 2. Проверка установки
```bash
# Проверка kubectl
kubectl version --client

# Проверка Helm
helm version

# Проверка Docker
docker --version
```

## Подготовка кластера

### 1. Создание локального кластера (Minikube)

```bash
# Установка Minikube
# Windows
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# macOS
brew install minikube

# Запуск кластера
minikube start --memory=8192 --cpus=4 --disk-size=50g

# Включение аддонов
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard
```

### 2. Настройка kubectl для Minikube
```bash
# Автоматически настраивается при запуске minikube
kubectl config use-context minikube

# Проверка кластера
kubectl cluster-info
kubectl get nodes
```

### 3. Настройка Docker registry (опционально)
```bash
# Настройка Minikube для использования локальных образов
eval $(minikube docker-env)

# Или использование внешнего registry
docker tag geolocation/frontend:latest your-registry.com/geolocation/frontend:latest
docker push your-registry.com/geolocation/frontend:latest
```

## Сборка Docker образов

### 1. Сборка всех образов

```bash
# Переход в директорию проекта
cd geolocation-system

# Сборка frontend
docker build -t geolocation/frontend:latest ./frontend/

# Сборка backend сервисов
docker build -t geolocation/api-gateway:latest ./backend/api-gateway/
docker build -t geolocation/auth-service:latest ./backend/auth-service/
docker build -t geolocation/image-service:latest ./backend/image-service/
docker build -t geolocation/neural-service:latest ./backend/neural-service/
docker build -t geolocation/coordinates-service:latest ./backend/coordinates-service/
docker build -t geolocation/export-service:latest ./backend/export-service/
docker build -t geolocation/notification-service:latest ./backend/notification-service/
```

### 2. Проверка образов
```bash
# Список образов
docker images | grep geolocation

# Тестирование образов
docker run --rm geolocation/frontend:latest --version
docker run --rm geolocation/api-gateway:latest --version
```

### 3. Создание скрипта сборки

```bash
# Создание скрипта build.sh
cat > build.sh << 'EOF'
#!/bin/bash

set -e

echo "🔨 Сборка Docker образов..."

# Frontend
echo "📦 Сборка frontend..."
docker build -t geolocation/frontend:latest ./frontend/

# Backend services
for service in api-gateway auth-service image-service neural-service coordinates-service export-service notification-service; do
    echo "📦 Сборка $service..."
    docker build -t geolocation/$service:latest ./backend/$service/
done

echo "✅ Все образы собраны успешно!"
docker images | grep geolocation
EOF

chmod +x build.sh
./build.sh
```

## Настройка секретов и конфигураций

### 1. Создание секретов

```bash
# Создание namespace
kubectl create namespace geolocation-system

# Секрет для PostgreSQL
kubectl create secret generic postgres-secret \
  --from-literal=password=your-secure-password \
  --namespace=geolocation-system

# Секрет для JWT
kubectl create secret generic jwt-secret \
  --from-literal=secret-key=your-jwt-secret-key \
  --namespace=geolocation-system

# Секрет для Google API
kubectl create secret generic google-api-secret \
  --from-literal=api-key=your-google-api-key \
  --namespace=geolocation-system

# Секрет для MinIO
kubectl create secret generic minio-secret \
  --from-literal=access-key=minioadmin \
  --from-literal=secret-key=minioadmin \
  --namespace=geolocation-system
```

### 2. Создание ConfigMap

```bash
# Создание ConfigMap для конфигурации
kubectl create configmap app-config \
  --from-literal=database-url=postgresql://postgres:password@postgres-service:5432/geolocation_db \
  --from-literal=redis-url=redis://redis-service:6379 \
  --from-literal=minio-endpoint=minio-service:9000 \
  --namespace=geolocation-system
```

### 3. Создание PersistentVolume для моделей

```yaml
# ml-models-pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: ml-models-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /data/ml-models
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: ml-models-pvc
  namespace: geolocation-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

```bash
# Применение PV
kubectl apply -f ml-models-pv.yaml
```

## Развертывание базы данных

### 1. PostgreSQL

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: geolocation-system
  labels:
    app: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        env:
        - name: POSTGRES_DB
          value: geolocation_db
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: geolocation-system
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: geolocation-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### 2. Redis

```yaml
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: geolocation-system
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:6-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: geolocation-system
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

### 3. MinIO

```yaml
# minio-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: minio
  namespace: geolocation-system
  labels:
    app: minio
spec:
  replicas: 1
  selector:
    matchLabels:
      app: minio
  template:
    metadata:
      labels:
        app: minio
    spec:
      containers:
      - name: minio
        image: minio/minio
        command: ["minio", "server", "/data"]
        env:
        - name: MINIO_ROOT_USER
          valueFrom:
            secretKeyRef:
              name: minio-secret
              key: access-key
        - name: MINIO_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: minio-secret
              key: secret-key
        ports:
        - containerPort: 9000
        - containerPort: 9001
        volumeMounts:
        - name: minio-storage
          mountPath: /data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: minio-storage
        persistentVolumeClaim:
          claimName: minio-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: minio-service
  namespace: geolocation-system
spec:
  selector:
    app: minio
  ports:
  - port: 9000
    targetPort: 9000
    name: api
  - port: 9001
    targetPort: 9001
    name: console
  type: ClusterIP

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: minio-pvc
  namespace: geolocation-system
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
```

### 4. Применение конфигураций базы данных

```bash
# Применение всех конфигураций
kubectl apply -f postgres-deployment.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f minio-deployment.yaml

# Проверка статуса
kubectl get pods -n geolocation-system
kubectl get services -n geolocation-system
```

## Развертывание микросервисов

### 1. Auth Service

```yaml
# auth-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: geolocation-system
  labels:
    app: auth-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: auth-service
  template:
    metadata:
      labels:
        app: auth-service
    spec:
      containers:
      - name: auth-service
        image: geolocation/auth-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: auth-service
  namespace: geolocation-system
spec:
  selector:
    app: auth-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 2. Neural Service

```yaml
# neural-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neural-service
  namespace: geolocation-system
  labels:
    app: neural-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: neural-service
  template:
    metadata:
      labels:
        app: neural-service
    spec:
      containers:
      - name: neural-service
        image: geolocation/neural-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: MODEL_PATH
          value: "/app/models/cvm-net"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: model-storage
          mountPath: /app/models
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: ml-models-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: neural-service
  namespace: geolocation-system
spec:
  selector:
    app: neural-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 3. Image Service

```yaml
# image-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: image-service
  namespace: geolocation-system
  labels:
    app: image-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: image-service
  template:
    metadata:
      labels:
        app: image-service
    spec:
      containers:
      - name: image-service
        image: geolocation/image-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: MINIO_ENDPOINT
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: minio-endpoint
        - name: MINIO_ACCESS_KEY
          valueFrom:
            secretKeyRef:
              name: minio-secret
              key: access-key
        - name: MINIO_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: minio-secret
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: image-service
  namespace: geolocation-system
spec:
  selector:
    app: image-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 4. Coordinates Service

```yaml
# coordinates-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: coordinates-service
  namespace: geolocation-system
  labels:
    app: coordinates-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: coordinates-service
  template:
    metadata:
      labels:
        app: coordinates-service
    spec:
      containers:
      - name: coordinates-service
        image: geolocation/coordinates-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: google-api-secret
              key: api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: coordinates-service
  namespace: geolocation-system
spec:
  selector:
    app: coordinates-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 5. Export Service

```yaml
# export-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: export-service
  namespace: geolocation-system
  labels:
    app: export-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: export-service
  template:
    metadata:
      labels:
        app: export-service
    spec:
      containers:
      - name: export-service
        image: geolocation/export-service:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: export-service
  namespace: geolocation-system
spec:
  selector:
    app: export-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 6. Notification Service

```yaml
# notification-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service
  namespace: geolocation-system
  labels:
    app: notification-service
spec:
  replicas: 2
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
    spec:
      containers:
      - name: notification-service
        image: geolocation/notification-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: notification-service
  namespace: geolocation-system
spec:
  selector:
    app: notification-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### 7. API Gateway

```yaml
# api-gateway-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: geolocation-system
  labels:
    app: api-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
      - name: api-gateway
        image: geolocation/api-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:8000"
        - name: IMAGE_SERVICE_URL
          value: "http://image-service:8000"
        - name: NEURAL_SERVICE_URL
          value: "http://neural-service:8000"
        - name: COORDINATES_SERVICE_URL
          value: "http://coordinates-service:8000"
        - name: EXPORT_SERVICE_URL
          value: "http://export-service:8000"
        - name: NOTIFICATION_SERVICE_URL
          value: "http://notification-service:8000"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: geolocation-system
spec:
  selector:
    app: api-gateway
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
```

### 8. Frontend

```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: geolocation-system
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: geolocation/frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "http://api-gateway:8000"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: geolocation-system
spec:
  selector:
    app: frontend
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
```

### 9. Применение всех сервисов

```bash
# Применение всех конфигураций
kubectl apply -f auth-service-deployment.yaml
kubectl apply -f neural-service-deployment.yaml
kubectl apply -f image-service-deployment.yaml
kubectl apply -f coordinates-service-deployment.yaml
kubectl apply -f export-service-deployment.yaml
kubectl apply -f notification-service-deployment.yaml
kubectl apply -f api-gateway-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Проверка статуса
kubectl get pods -n geolocation-system
kubectl get services -n geolocation-system
```

## Настройка Ingress

### 1. Установка NGINX Ingress Controller

```bash
# Установка через Helm
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer
```

### 2. Создание Ingress ресурса

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: geolocation-ingress
  namespace: geolocation-system
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  rules:
  - host: geolocation.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8000
```

### 3. Настройка DNS (для Minikube)

```bash
# Получение IP адреса
minikube ip

# Добавление в hosts файл
echo "$(minikube ip) geolocation.local" | sudo tee -a /etc/hosts

# Windows
echo "$(minikube ip) geolocation.local" >> C:\Windows\System32\drivers\etc\hosts
```

### 4. Применение Ingress

```bash
kubectl apply -f ingress.yaml

# Проверка Ingress
kubectl get ingress -n geolocation-system
```

## Мониторинг и логирование

### 1. Установка Prometheus

```bash
# Добавление Helm репозитория
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Установка Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=admin
```

### 2. Установка Grafana

```bash
# Grafana уже включена в kube-prometheus-stack
# Доступ: http://localhost:3000
# Логин: admin
# Пароль: admin
```

### 3. Настройка мониторинга приложения

```yaml
# service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: geolocation-services
  namespace: geolocation-system
spec:
  selector:
    matchLabels:
      app: api-gateway
  endpoints:
  - port: 8000
    path: /metrics
```

### 4. Применение мониторинга

```bash
kubectl apply -f service-monitor.yaml
```

## Масштабирование

### 1. Горизонтальное масштабирование (HPA)

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: geolocation-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Вертикальное масштабирование (VPA)

```bash
# Установка VPA
kubectl apply -f https://github.com/kubernetes/autoscaler/releases/download/vertical-pod-autoscaler-0.13.0/vpa-release.yaml

# Создание VPA для neural-service
cat > vpa.yaml << EOF
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: neural-service-vpa
  namespace: geolocation-system
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: neural-service
  updatePolicy:
    updateMode: "Auto"
EOF

kubectl apply -f vpa.yaml
```

### 3. Применение масштабирования

```bash
kubectl apply -f hpa.yaml
kubectl apply -f vpa.yaml

# Проверка HPA
kubectl get hpa -n geolocation-system

# Проверка VPA
kubectl get vpa -n geolocation-system
```

## Полный скрипт развертывания

```bash
#!/bin/bash
# deploy-k8s.sh

set -e

echo "🚀 Развертывание системы геолокации в Kubernetes..."

# 1. Создание namespace
echo "📦 Создание namespace..."
kubectl create namespace geolocation-system --dry-run=client -o yaml | kubectl apply -f -

# 2. Создание секретов
echo "🔐 Создание секретов..."
kubectl create secret generic postgres-secret \
  --from-literal=password=your-secure-password \
  --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic jwt-secret \
  --from-literal=secret-key=your-jwt-secret-key \
  --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic google-api-secret \
  --from-literal=api-key=your-google-api-key \
  --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -

# 3. Создание ConfigMap
echo "⚙️ Создание ConfigMap..."
kubectl create configmap app-config \
  --from-literal=database-url=postgresql://postgres:password@postgres-service:5432/geolocation_db \
  --from-literal=redis-url=redis://redis-service:6379 \
  --from-literal=minio-endpoint=minio-service:9000 \
  --namespace=geolocation-system --dry-run=client -o yaml | kubectl apply -f -

# 4. Применение всех конфигураций
echo "🔧 Применение конфигураций..."
kubectl apply -f infrastructure/kubernetes/

# 5. Ожидание готовности подов
echo "⏳ Ожидание готовности подов..."
kubectl wait --for=condition=ready pod -l app=postgres -n geolocation-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n geolocation-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=minio -n geolocation-system --timeout=300s

# 6. Проверка статуса
echo "✅ Проверка статуса..."
kubectl get pods -n geolocation-system
kubectl get services -n geolocation-system

echo "🎉 Развертывание завершено!"
echo "🌐 Доступ к приложению:"
echo "   Frontend: http://geolocation.local"
echo "   API: http://geolocation.local/api"
```

## Устранение неполадок

### 1. Проверка логов

```bash
# Логи конкретного пода
kubectl logs -f deployment/api-gateway -n geolocation-system

# Логи всех подов в namespace
kubectl logs -f -l app=api-gateway -n geolocation-system

# Предыдущие логи
kubectl logs --previous deployment/api-gateway -n geolocation-system
```

### 2. Проверка событий

```bash
# События в namespace
kubectl get events -n geolocation-system --sort-by='.lastTimestamp'

# События конкретного ресурса
kubectl describe pod <pod-name> -n geolocation-system
```

### 3. Проверка ресурсов

```bash
# Использование ресурсов
kubectl top pods -n geolocation-system
kubectl top nodes

# Описание ресурсов
kubectl describe pod <pod-name> -n geolocation-system
kubectl describe service <service-name> -n geolocation-system
```

### 4. Отладка сети

```bash
# Проверка DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup postgres-service

# Проверка подключения
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -qO- http://api-gateway:8000/health
```

### 5. Перезапуск сервисов

```bash
# Перезапуск deployment
kubectl rollout restart deployment/api-gateway -n geolocation-system

# Проверка статуса rollout
kubectl rollout status deployment/api-gateway -n geolocation-system

# Откат к предыдущей версии
kubectl rollout undo deployment/api-gateway -n geolocation-system
```

### 6. Очистка ресурсов

```bash
# Удаление всех ресурсов
kubectl delete namespace geolocation-system

# Удаление конкретных ресурсов
kubectl delete deployment api-gateway -n geolocation-system
kubectl delete service api-gateway -n geolocation-system
```

## Полезные команды

```bash
# Просмотр всех ресурсов
kubectl get all -n geolocation-system

# Порт-форвардинг для локального доступа
kubectl port-forward service/api-gateway 8000:8000 -n geolocation-system
kubectl port-forward service/frontend 3000:3000 -n geolocation-system

# Подключение к поду
kubectl exec -it deployment/api-gateway -n geolocation-system -- /bin/bash

# Копирование файлов
kubectl cp local-file deployment/api-gateway:/app/file -n geolocation-system

# Масштабирование
kubectl scale deployment api-gateway --replicas=5 -n geolocation-system
```

## Заключение

Этот гайд предоставляет полную инструкцию по развертыванию системы геолокации в Kubernetes. Следуя этим шагам, вы сможете:

1. ✅ Настроить локальный кластер Kubernetes
2. ✅ Собрать и развернуть все Docker образы
3. ✅ Настроить базы данных и хранилища
4. ✅ Развернуть все микросервисы
5. ✅ Настроить мониторинг и логирование
6. ✅ Обеспечить масштабируемость системы

Система будет доступна по адресу `http://geolocation.local` с полным функционалом распознавания географических координат по фотографиям.
