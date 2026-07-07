# Guia Completo de Deploy - CrachApp no Digital Ocean

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Criar Droplet no Digital Ocean](#criar-droplet)
3. [Configurar Servidor](#configurar-servidor)
4. [Preparar Aplicação](#preparar-aplicação)
5. [Deploy com Docker Compose](#deploy)
6. [Configurar SSL/TLS](#ssl)
7. [Monitoramento e Manutenção](#monitoramento)
8. [Troubleshooting](#troubleshooting)

---

## Pré-requisitos

### Contas e Credenciais
- Conta Digital Ocean ativa
- Domínio registrado (ex: crachapp.com.br)
- Acesso SSH
- Variáveis de ambiente preparadas:
  - `DATABASE_URL`
  - `SECRET_KEY`
  - `CLOUDINARY_URL`
  - `MERCADOPAGO_ACCESS_TOKEN`
  - `POSTGRES_PASSWORD`
  - `REDIS_PASSWORD`
  - `APP_URL`

---

## 1. Criar Droplet no Digital Ocean

### 1.1 Escolher Configuração Recomendada

```
- Imagem: Ubuntu 22.04 LTS x64
- Tamanho: $24/mês (4GB RAM, 2 vCPU, 80GB SSD)
- Datacenter: Região mais próxima (ex: São Paulo)
- SSH Key: Adicionar sua chave pública
- Hostname: crachapp-prod
```

### 1.2 Aumentar Espaço de Troca (Swap)

```bash
# Conectar via SSH
ssh root@seu_ip

# Criar 2GB de swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

---

## 2. Configurar Servidor

### 2.1 Atualizar Sistema

```bash
apt update && apt upgrade -y
```

### 2.2 Instalar Docker e Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

### 2.3 Criar Usuário de Deploy

```bash
# Criar usuário
useradd -m -s /bin/bash deploy
usermod -aG docker deploy

# Mudar para o usuário
su - deploy
```

### 2.4 Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP e HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar regras
sudo ufw status
```

---

## 3. Preparar Aplicação

### 3.1 Clonar Repositório

```bash
cd /home/deploy
git clone https://github.com/seu-repo/auto_cracha.git
cd auto_cracha
```

### 3.2 Criar Arquivo .env

```bash
cat > .env << EOF
# Database
POSTGRES_USER=crachapp
POSTGRES_PASSWORD=$(openssl rand -base64 32)
POSTGRES_DB=crachapp

# Redis
REDIS_PASSWORD=$(openssl rand -base64 32)

# Application
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
APP_URL=https://crachapp.com.br
NEXT_PUBLIC_API_URL=https://crachapp.com.br/api

# Integrações
CLOUDINARY_URL=cloudinary://your_key:your_secret@your_cloud
MERCADOPAGO_ACCESS_TOKEN=seu_token_mercado_pago

# Database URL (construído abaixo)
DATABASE_URL=postgresql://crachapp:${POSTGRES_PASSWORD}@postgres:5432/crachapp
EOF
```

### 3.3 Verificar Estrutura de Diretórios

```bash
# Garantir que nginx/ssl existe
mkdir -p nginx/ssl

# Copiar diretório .gitkeep para ssl (será preenchido após SSL)
touch nginx/ssl/.gitkeep
```

---

## 4. Deploy com Docker Compose

### 4.1 Construir e Iniciar Containers

```bash
cd /home/deploy/auto_cracha

# Build das imagens
docker-compose build

# Iniciar containers em background
docker-compose up -d

# Verificar status
docker-compose ps

# Verificar logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 4.2 Verificar Saúde da Aplicação

```bash
# Esperar 30 segundos para warm up
sleep 30

# Testar health endpoint
curl http://localhost:8000/health

# Testar frontend
curl -I http://localhost:80
```

### 4.3 Dados Iniciais (Seed)

O script de seed roda automaticamente no início do container backend:

```bash
# Ver se dados foram criados
docker-compose exec postgres psql -U crachapp -d crachapp -c "SELECT COUNT(*) FROM usuarios;"

# Credenciais padrão (geradas após seed):
# Admin: admin@crachapp.com.br / Admin@123456
# Tenant: teste@empresa.com.br / Teste@123456
```

---

## 5. Configurar SSL/TLS

### 5.1 Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 5.2 Gerar Certificado Let's Encrypt

```bash
# Parar nginx temporariamente
docker-compose stop nginx

# Gerar certificado
sudo certbot certonly --standalone -d crachapp.com.br -d www.crachapp.com.br

# Certificados estarão em:
# /etc/letsencrypt/live/crachapp.com.br/

# Copiar para nginx/ssl
sudo cp /etc/letsencrypt/live/crachapp.com.br/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/crachapp.com.br/privkey.pem nginx/ssl/key.pem
sudo chown deploy:deploy nginx/ssl/*
```

### 5.3 Habilitar HTTPS no Nginx

```bash
# Editar nginx/conf.d/crachapp.conf
# Descomentar a seção HTTPS e comentar a seção HTTP

# Ou usar sed para automatizar:
sed -i 's/# server {/server {/g; s/# *listen 443/listen 443/g; s/# *ssl_/ssl_/g; s/# *add_header Strict/add_header Strict/g' nginx/conf.d/crachapp.conf

# Adicionar redirecionamento de HTTP para HTTPS
sed -i '1s/^/# HTTP to HTTPS redirect\nserver {\n    listen 80;\n    server_name _;\n    return 301 https:\/\/$server_name$request_uri;\n}\n\n/' nginx/conf.d/crachapp.conf
```

### 5.4 Reiniciar Nginx

```bash
# Recarregar nginx
docker-compose restart nginx

# Verificar SSL
curl -I https://crachapp.com.br
```

### 5.5 Auto-renovação de Certificado

```bash
# Criar script de renovação
sudo tee /usr/local/bin/renew-cert.sh > /dev/null << EOF
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/crachapp.com.br/fullchain.pem /home/deploy/auto_cracha/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/crachapp.com.br/privkey.pem /home/deploy/auto_cracha/nginx/ssl/key.pem
chown deploy:deploy /home/deploy/auto_cracha/nginx/ssl/*
cd /home/deploy/auto_cracha && docker-compose restart nginx
EOF

# Tornar executável
sudo chmod +x /usr/local/bin/renew-cert.sh

# Adicionar ao crontab para rodar diariamente
sudo crontab -e

# Adicionar esta linha:
# 0 2 * * * /usr/local/bin/renew-cert.sh >> /var/log/certbot-renew.log 2>&1
```

---

## 6. Monitoramento e Manutenção

### 6.1 Verificar Status

```bash
# Status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Logs específicos
docker-compose logs backend
docker-compose logs postgres
```

### 6.2 Backup do Banco de Dados

```bash
# Backup manual
docker-compose exec postgres pg_dump -U crachapp crachapp > backup_$(date +%Y%m%d_%H%M%S).sql

# Restaurar de backup
cat backup_20240101_000000.sql | docker-compose exec -T postgres psql -U crachapp crachapp

# Backup automatizado (cron)
# 0 3 * * * cd /home/deploy/auto_cracha && docker-compose exec -T postgres pg_dump -U crachapp crachapp | gzip > /home/deploy/backups/db_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz
```

### 6.3 Atualizar Aplicação

```bash
cd /home/deploy/auto_cracha

# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Check logs
docker-compose logs -f backend
```

### 6.4 Monitoramento com DigitalOcean Monitoring

```bash
# Instalar agent
curl -sSL https://repos.insights.digitalocean.com/install.sh | sh

# Reiniciar Docker
systemctl restart docker
```

---

## 7. Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs backend

# Se banco não conecta, aguardar:
docker-compose logs postgres

# Recriar volume (CUIDADO - apaga dados)
docker-compose down -v
docker-compose up -d
```

### Erro de permissão SSL

```bash
# Verificar permissões
ls -la nginx/ssl/

# Corrigir
sudo chown deploy:deploy nginx/ssl/*
sudo chmod 644 nginx/ssl/*.pem
```

### Migração de banco falha

```bash
# Rollback manual
docker-compose exec backend alembic downgrade -1

# Executar específica
docker-compose exec backend alembic upgrade 0005

# Ver histórico
docker-compose exec backend alembic history
```

### Espaço em disco cheio

```bash
# Limpar Docker
docker system prune -a

# Limpar logs
docker exec $(docker ps -q) sh -c 'truncate -s 0 /var/log/app.log'

# Ver uso
du -sh /var/lib/docker
```

### Email não funciona (Reset de senha)

```bash
# Verificar credenciais SMTP
docker-compose logs backend | grep "email\|smtp"

# Testar conexão
docker-compose exec backend python -c "
import smtplib
# Adicionar teste de SMTP aqui
"
```

---

## 8. Checklist Final de Deploy

- [ ] Servidor criado e acessível via SSH
- [ ] Docker e Docker Compose instalados
- [ ] Arquivo .env configurado com todas as variáveis
- [ ] Docker Compose build bem-sucedido
- [ ] Containers iniciados e saudáveis
- [ ] Database migrations executadas
- [ ] Seed data criada
- [ ] Frontend acessível em http://localhost:80
- [ ] Backend respondendo em http://localhost:8000/health
- [ ] SSL/TLS certificado instalado
- [ ] HTTPS redirecionando corretamente
- [ ] Domínio apontando para o Droplet
- [ ] Backups configurados
- [ ] Monitoring ativo
- [ ] Logs sendo coletados

---

## Suporte e Contato

Para problemas não listados aqui:
1. Verificar logs: `docker-compose logs -f`
2. Consultar documentação oficial dos serviços
3. Criar issue no repositório

**Versão do Guia:** 1.0
**Data:** 2024-06-22
**Aplicação:** CrachApp v1.0.0
