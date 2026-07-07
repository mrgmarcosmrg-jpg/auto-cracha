#!/bin/bash
# Script de deploy automático via webhook
# Este arquivo é executado pelo webhook listener

REPO_PATH="/home/deploy/auto_cracha"

echo "🚀 Deploy automático iniciado em $(date)"

# Ir para o repositório
cd $REPO_PATH

# Atualizar código do GitHub
git fetch origin main
git reset --hard origin/main

echo "✅ Código atualizado do GitHub"

# Rebuild e restart containers
cd $REPO_PATH/auto_cracha/frontend-web
docker-compose -f ../../docker-compose.yml build --no-cache frontend
docker-compose -f ../../docker-compose.yml up -d frontend

echo "✅ Frontend atualizado e reiniciado"
echo "🎉 Deploy concluído em $(date)"
