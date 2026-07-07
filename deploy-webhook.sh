#!/bin/bash
# Script de webhook para deploy automático
# Executar quando há novo push no GitHub

REPO_PATH="/home/deploy/auto_cracha"
FRONTEND_PATH="$REPO_PATH/frontend-web"
BACKEND_PATH="$REPO_PATH/backend"

echo "🚀 Deploy automático iniciado em $(date)"

# Atualizar código
cd $REPO_PATH
git fetch origin main
git reset --hard origin/main

echo "✅ Código atualizado"

# Rebuild frontend
cd $FRONTEND_PATH
docker-compose -f $REPO_PATH/docker-compose.yml build --no-cache frontend

# Restart containers
docker-compose -f $REPO_PATH/docker-compose.yml up -d frontend

echo "✅ Frontend atualizado e reiniciado"
echo "🎉 Deploy concluído!"
