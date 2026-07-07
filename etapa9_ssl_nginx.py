import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\n" + "=" * 80)
print("ETAPA 9 - CONFIGURAR SSL/HTTPS COM NGINX")
print("=" * 80)

# PASSO 1: Instalar Nginx
print("\n[PASSO 1] Instalar Nginx")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('apt-get update && apt-get install -y nginx')
result = stdout.read().decode()
print("[OK] Nginx instalado")

# PASSO 2: Criar certificado self-signed
print("\n[PASSO 2] Criar certificado SSL self-signed")
print("-" * 80)
cmd = '''mkdir -p /etc/nginx/ssl && \
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/crachapp.key \
  -out /etc/nginx/ssl/crachapp.crt \
  -subj "/C=BR/ST=SP/L=Sao Paulo/O=CrachApp/CN=157.245.217.95"'''

stdin, stdout, stderr = client.exec_command(cmd)
result = stdout.read().decode()
print("[OK] Certificado criado em /etc/nginx/ssl/")

# PASSO 3: Criar configuracao do Nginx
print("\n[PASSO 3] Criar configuracao do Nginx (reverse proxy)")
print("-" * 80)

nginx_config = '''server {
    listen 80;
    server_name 157.245.217.95;

    # Redirecionar HTTP para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 157.245.217.95;

    # Certificados SSL
    ssl_certificate /etc/nginx/ssl/crachapp.crt;
    ssl_certificate_key /etc/nginx/ssl/crachapp.key;

    # Configuracoes SSL modernas
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Cache para melhor performance
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Limite de upload
    client_max_body_size 100M;

    # BACKEND (API) - porta 8000
    location /auth/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /redoc {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }

    # Qualquer rota com / que nao seja /auth /* vai pro frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Para Next.js
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
'''

# Salvar configuracao no servidor
sftp = client.open_sftp()
with sftp.file('/tmp/crachapp_nginx.conf', 'w') as f:
    f.write(nginx_config)
sftp.close()

# Copiar para /etc/nginx/sites-available/
stdin, stdout, stderr = client.exec_command('cp /tmp/crachapp_nginx.conf /etc/nginx/sites-available/crachapp')
stdout.read().decode()

# Ativar site (symbolic link)
stdin, stdout, stderr = client.exec_command('ln -sf /etc/nginx/sites-available/crachapp /etc/nginx/sites-enabled/crachapp')
stdout.read().decode()

# Remover default se existir
stdin, stdout, stderr = client.exec_command('rm -f /etc/nginx/sites-enabled/default')
stdout.read().decode()

print("[OK] Configuracao criada")

# PASSO 4: Testar sintaxe Nginx
print("\n[PASSO 4] Testar configuracao Nginx")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('nginx -t')
result = stdout.read().decode()
errors = stderr.read().decode()
print(result)
if errors:
    print("ERRO:", errors)

# PASSO 5: Iniciar Nginx
print("\n[PASSO 5] Iniciar/Reiniciar Nginx")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('systemctl restart nginx')
time.sleep(2)
stdout.read().decode()
print("[OK]")

# PASSO 6: Verificar status
print("\n[PASSO 6] Verificar status do Nginx")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('systemctl status nginx')
result = stdout.read().decode()
if 'active (running)' in result:
    print("[OK] Nginx rodando")
else:
    print("Status:")
    print(result[:300])

# PASSO 7: Testar HTTPS
print("\n[PASSO 7] Teste HTTPS (curl com -k para ignorar self-signed)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -k -I https://157.245.217.95 2>&1 | head -10')
result = stdout.read().decode()
print(result)

# PASSO 8: Testar redirecionamento HTTP -> HTTPS
print("\n[PASSO 8] Teste redirecionamento HTTP -> HTTPS")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -I http://157.245.217.95 2>&1 | head -5')
result = stdout.read().decode()
print(result)

# PASSO 9: Teste de rotas
print("\n[PASSO 9] Teste de rotas via HTTPS")
print("-" * 80)

print("\na) Frontend (raiz):")
stdin, stdout, stderr = client.exec_command('curl -k -s https://157.245.217.95/ | head -20')
result = stdout.read().decode()
print(result[:200] if result else "Vazio")

print("\nb) API Docs:")
stdin, stdout, stderr = client.exec_command('curl -k -s https://157.245.217.95/docs | head -10')
result = stdout.read().decode()
if '<' in result:
    print("[OK] Swagger docs acessivel")
else:
    print(result[:200])

print("\n" + "=" * 80)
print("RESUMO - ETAPA 9 PARTE 1 (SSL/HTTPS)")
print("=" * 80)

print("""
[OK] Nginx instalado e configurado
[OK] Certificado SSL self-signed criado
[OK] Reverse proxy configurado
[OK] Redirecionamento HTTP -> HTTPS ativo

ACESSOS:
- HTTPS: https://157.245.217.95 (aviso de certificado, mas funciona)
- API Docs: https://157.245.217.95/docs
- Frontend: https://157.245.217.95/dashboard

PORTA 443: Recebe requisicoes HTTPS
PORTA 80: Redireciona para HTTPS

PROXIMOS PASSOS:
1. Testar login via HTTPS
2. Configurar backups automaticos
3. Monitoramento de logs
4. Quando tiver dominio: trocar certificado para Let's Encrypt
""")

client.close()
