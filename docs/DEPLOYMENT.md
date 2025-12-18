# Deployment Guide

## Overview

This guide covers deploying Behflow in various environments, from local development to production cloud platforms.

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space
- Domain name (for production)
- SSL certificate (for production)

## Local Development

### Docker Compose Setup

```bash
# Clone repository
git clone https://github.com/artaasd95/Behflow.git
cd Behflow

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Configuration

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/behflow

# Backend
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-change-this

# LLM Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Scheduler
RESCHEDULE_TASKS_SCHEDULE=0 0 * * *

# Frontend
FRONTEND_PORT=8080
```

## Production Deployment

### Option 1: Docker Swarm

#### Initialize Swarm

```bash
# On manager node
docker swarm init --advertise-addr <MANAGER-IP>

# On worker nodes
docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

#### Deploy Stack

```yaml
# docker-stack.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: behflow
      POSTGRES_USER: behflow
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - behflow_network
    secrets:
      - db_password
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager
      restart_policy:
        condition: on-failure

  backend:
    image: behflow/backend:latest
    environment:
      DATABASE_URL: postgresql://behflow:@db:5432/behflow
      SECRET_KEY_FILE: /run/secrets/secret_key
      OPENAI_API_KEY_FILE: /run/secrets/openai_key
    networks:
      - behflow_network
    secrets:
      - db_password
      - secret_key
      - openai_key
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.backend.rule=Host(`api.behflow.example.com`)"
        - "traefik.http.services.backend.loadbalancer.server.port=8000"

  frontend:
    image: behflow/frontend:latest
    networks:
      - behflow_network
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.frontend.rule=Host(`behflow.example.com`)"

  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker.swarmMode=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik_certs:/letsencrypt
    networks:
      - behflow_network
    deploy:
      placement:
        constraints:
          - node.role == manager

volumes:
  db_data:
  traefik_certs:

networks:
  behflow_network:
    driver: overlay
    attachable: true

secrets:
  db_password:
    external: true
  secret_key:
    external: true
  openai_key:
    external: true
```

#### Create Secrets

```bash
# Create secrets
echo "your-db-password" | docker secret create db_password -
echo "your-secret-key" | docker secret create secret_key -
echo "sk-your-openai-key" | docker secret create openai_key -

# Deploy stack
docker stack deploy -c docker-stack.yml behflow

# Check services
docker stack services behflow

# Scale service
docker service scale behflow_backend=5
```

### Option 2: Kubernetes

#### Namespace

```yaml
# namespace.yml
apiVersion: v1
kind: Namespace
metadata:
  name: behflow
```

#### ConfigMap

```yaml
# configmap.yml
apiVersion: v1
kind: ConfigMap
metadata:
  name: behflow-config
  namespace: behflow
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  RESCHEDULE_TASKS_SCHEDULE: "0 0 * * *"
```

#### Secrets

```yaml
# secrets.yml
apiVersion: v1
kind: Secret
metadata:
  name: behflow-secrets
  namespace: behflow
type: Opaque
stringData:
  database-url: postgresql://behflow:password@postgres:5432/behflow
  secret-key: your-secret-key-here
  openai-api-key: sk-your-key-here
```

#### PostgreSQL Deployment

```yaml
# postgres-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: behflow
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
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: behflow
        - name: POSTGRES_USER
          value: behflow
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: behflow-secrets
              key: database-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: behflow
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: behflow
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

#### Backend Deployment

```yaml
# backend-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: behflow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: behflow/backend:latest
        envFrom:
        - configMapRef:
            name: behflow-config
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: behflow-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: behflow-secrets
              key: secret-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: behflow-secrets
              key: openai-api-key
        ports:
        - containerPort: 8000
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
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: behflow
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
```

#### Frontend Deployment

```yaml
# frontend-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: behflow
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
        image: behflow/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: behflow
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
```

#### Ingress

```yaml
# ingress.yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: behflow-ingress
  namespace: behflow
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - behflow.example.com
    - api.behflow.example.com
    secretName: behflow-tls
  rules:
  - host: behflow.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
  - host: api.behflow.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
```

#### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f namespace.yml
kubectl apply -f configmap.yml
kubectl apply -f secrets.yml
kubectl apply -f postgres-deployment.yml
kubectl apply -f backend-deployment.yml
kubectl apply -f frontend-deployment.yml
kubectl apply -f ingress.yml

# Check status
kubectl get all -n behflow

# View logs
kubectl logs -f deployment/backend -n behflow

# Scale deployment
kubectl scale deployment/backend --replicas=5 -n behflow
```

### Option 3: Cloud Platforms

#### AWS (ECS)

```bash
# Install AWS CLI and ECS CLI
pip install awscli ecs-cli

# Configure ECS CLI
ecs-cli configure --cluster behflow-cluster --region us-east-1 --default-launch-type FARGATE

# Create cluster
ecs-cli up --cluster-config behflow --capability-iam

# Deploy services
ecs-cli compose --file docker-compose.yml --project-name behflow service up --launch-type FARGATE
```

#### Google Cloud Platform (Cloud Run)

```bash
# Build and push images
gcloud builds submit --tag gcr.io/PROJECT_ID/behflow-backend ./src/backend
gcloud builds submit --tag gcr.io/PROJECT_ID/behflow-frontend ./src/frontend

# Deploy backend
gcloud run deploy behflow-backend \
  --image gcr.io/PROJECT_ID/behflow-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy frontend
gcloud run deploy behflow-frontend \
  --image gcr.io/PROJECT_ID/behflow-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Azure (Container Apps)

```bash
# Create resource group
az group create --name behflow-rg --location eastus

# Create container registry
az acr create --resource-group behflow-rg --name behflowregistry --sku Basic

# Build and push images
az acr build --registry behflowregistry --image behflow-backend:latest ./src/backend
az acr build --registry behflowregistry --image behflow-frontend:latest ./src/frontend

# Create container app environment
az containerapp env create \
  --name behflow-env \
  --resource-group behflow-rg \
  --location eastus

# Deploy backend
az containerapp create \
  --name behflow-backend \
  --resource-group behflow-rg \
  --environment behflow-env \
  --image behflowregistry.azurecr.io/behflow-backend:latest \
  --target-port 8000 \
  --ingress external

# Deploy frontend
az containerapp create \
  --name behflow-frontend \
  --resource-group behflow-rg \
  --environment behflow-env \
  --image behflowregistry.azurecr.io/behflow-frontend:latest \
  --target-port 80 \
  --ingress external
```

## SSL/TLS Configuration

### Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d behflow.example.com -d api.behflow.example.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name behflow.example.com;

    ssl_certificate /etc/letsencrypt/live/behflow.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/behflow.example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 443 ssl http2;
    server_name api.behflow.example.com;

    ssl_certificate /etc/letsencrypt/live/behflow.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/behflow.example.com/privkey.pem;

    location / {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Prometheus & Grafana

```yaml
# monitoring-stack.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  prometheus_data:
  grafana_data:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'behflow-backend'
    static_configs:
      - targets: ['backend:8000']
```

## Backup Strategy

### Database Backup

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="behflow"
S3_BUCKET="s3://behflow-backups"

# Create backup
docker exec behflow-db pg_dump -U postgres $DB_NAME | gzip > $BACKUP_DIR/behflow_$DATE.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/behflow_$DATE.sql.gz $S3_BUCKET/

# Keep only last 30 days locally
find $BACKUP_DIR -name "behflow_*.sql.gz" -mtime +30 -delete

# Verify backup
if [ $? -eq 0 ]; then
    echo "Backup successful: behflow_$DATE.sql.gz"
else
    echo "Backup failed!"
    exit 1
fi
```

### Automated Backup with Cron

```bash
# Add to crontab
0 2 * * * /opt/behflow/backup.sh >> /var/log/behflow-backup.log 2>&1
```

## High Availability

### Load Balancing

```nginx
# nginx-lb.conf
upstream backend_servers {
    least_conn;
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend_servers;
        proxy_next_upstream error timeout http_502 http_503 http_504;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Replication

```yaml
# postgres-primary.yml
version: '3.8'

services:
  postgres-primary:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: behflow
      POSTGRES_USER: behflow
      POSTGRES_PASSWORD: password
      POSTGRES_INITDB_ARGS: "-c wal_level=replica"
    command: |
      postgres
      -c wal_level=replica
      -c max_wal_senders=3
      -c max_replication_slots=3
    volumes:
      - pg_primary_data:/var/lib/postgresql/data

volumes:
  pg_primary_data:
```

## Troubleshooting

### Common Issues

**Issue**: Database connection refused

```bash
# Check database container
docker-compose logs db

# Verify network connectivity
docker-compose exec backend ping db

# Check database is ready
docker-compose exec db pg_isready -U postgres
```

**Issue**: High memory usage

```bash
# Check container stats
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

**Issue**: SSL certificate expired

```bash
# Renew certificate
certbot renew --force-renewal

# Reload nginx
docker-compose exec frontend nginx -s reload
```

## Performance Tuning

### Database Optimization

```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 16MB
maintenance_work_mem = 128MB
max_connections = 100
```

### Backend Optimization

```python
# Use connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True
)

# Enable caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_user_by_id(user_id: str):
    # ...
```

### Frontend Optimization

```nginx
# Enable gzip compression
gzip on;
gzip_types text/css application/javascript application/json;

# Browser caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Security Hardening

### Firewall Rules

```bash
# UFW (Ubuntu)
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw deny 5432/tcp
ufw enable
```

### Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## Scaling Strategies

### Horizontal Scaling

```bash
# Docker Swarm
docker service scale behflow_backend=10

# Kubernetes
kubectl scale deployment/backend --replicas=10 -n behflow
```

### Vertical Scaling

```yaml
# Increase resources
resources:
  limits:
    memory: "4Gi"
    cpu: "2000m"
  requests:
    memory: "2Gi"
    cpu: "1000m"
```

## Rollback Procedure

```bash
# Docker Swarm
docker service rollback behflow_backend

# Kubernetes
kubectl rollout undo deployment/backend -n behflow

# Docker Compose
docker-compose down
git checkout previous-version
docker-compose up -d
```
