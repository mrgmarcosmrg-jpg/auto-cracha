#!/bin/bash
set -e

echo "=== ETAPA 1: Verificando arquivo main.py ==="
ls -la /home/deploy/auto_cracha/backend/main.py

echo ""
echo "=== ETAPA 2: Parando container backend ==="
docker stop crachapp_backend || true
docker rm crachapp_backend || true

echo ""
echo "=== ETAPA 3: Reconstruindo imagem ==="
cd /home/deploy/auto_cracha/backend
docker build -t crachapp_backend:latest .

echo ""
echo "=== ETAPA 4: Iniciando novo container ==="
docker run -d \
  --name crachapp_backend \
  --network crachapp_network \
  -p 8000:8000 \
  --env-file /home/deploy/auto_cracha/.env \
  -v /home/deploy/auto_cracha/backend/app:/app/app \
  -v /home/deploy/auto_cracha/backend/alembic:/app/alembic \
  crachapp_backend:latest

echo ""
echo "=== ETAPA 5: Testando health endpoint ==="
sleep 5
curl -s http://localhost:8000/health | jq . || echo "Falha ao testar health endpoint"

echo ""
echo "=== DEPLOY BACKEND CONCLUÍDO ==="
date
