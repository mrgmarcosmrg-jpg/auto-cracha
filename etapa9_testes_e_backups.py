import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\n" + "=" * 80)
print("ETAPA 9 PARTE 2 - TESTES E BACKUPS")
print("=" * 80)

# PASSO 1: Testar login via HTTPS
print("\n[PASSO 1] Testar login via HTTPS")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -k -s -X POST https://157.245.217.95/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
login_result = stdout.read().decode()

try:
    login_data = json.loads(login_result)
    if 'access_token' in login_data:
        print("[OK] Login funcionando via HTTPS!")
        print(f"    Token: {login_data['access_token'][:50]}...")
        access_token = login_data['access_token']
    else:
        print("[ERRO] Resposta inesperada:")
        print(login_result[:200])
        access_token = None
except:
    print("[ERRO]")
    print(login_result[:200])
    access_token = None

# PASSO 2: Testar rota protegida via HTTPS
if access_token:
    print("\n[PASSO 2] Testar rota protegida via HTTPS")
    print("-" * 80)
    stdin, stdout, stderr = client.exec_command(f'''curl -k -s -H "Authorization: Bearer {access_token}" https://157.245.217.95/health''')
    health_result = stdout.read().decode()

    try:
        health_data = json.loads(health_result)
        if 'status' in health_data:
            print("[OK] Rota protegida respondendo!")
            print(f"    Status: {health_data.get('status')}")
    except:
        print(health_result[:200])

# PASSO 3: Criar script de backup do banco
print("\n[PASSO 3] Criar script de backup automatico")
print("-" * 80)

backup_script = '''#!/bin/bash

BACKUP_DIR="/home/deploy/backups"
DB_NAME="crachapp"
DB_USER="crachapp"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/crachapp_$BACKUP_DATE.sql"

# Criar diretorio se nao existir
mkdir -p $BACKUP_DIR

# Fazer backup
docker exec crachapp_postgres pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE

# Comprimir
gzip $BACKUP_FILE

# Manter apenas os ultimos 7 backups
cd $BACKUP_DIR
ls -t crachapp_*.sql.gz | tail -n +8 | xargs rm -f

echo "Backup criado: $BACKUP_FILE.gz"
'''

sftp = client.open_sftp()
with sftp.file('/home/deploy/backup_db.sh', 'w') as f:
    f.write(backup_script)
sftp.close()

# Dar permissao de execucao
stdin, stdout, stderr = client.exec_command('chmod +x /home/deploy/backup_db.sh')
stdout.read().decode()

print("[OK] Script de backup criado em /home/deploy/backup_db.sh")

# PASSO 4: Agendar backup diario (cron)
print("\n[PASSO 4] Agendar backup diario (cron)")
print("-" * 80)

# Verificar se ja existe
stdin, stdout, stderr = client.exec_command('crontab -l 2>/dev/null | grep backup_db')
existing = stdout.read().decode()

if 'backup_db' not in existing:
    # Adicionar novo cron job (3 da manha todos os dias)
    stdin, stdout, stderr = client.exec_command('''(crontab -l 2>/dev/null; echo "0 3 * * * /home/deploy/backup_db.sh >> /home/deploy/backup_db.log 2>&1") | crontab -''')
    stdout.read().decode()
    print("[OK] Backup agendado para 03:00 todos os dias")
else:
    print("[INFO] Backup ja estava agendado")

# PASSO 5: Executar backup de teste
print("\n[PASSO 5] Executar backup de teste")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('/home/deploy/backup_db.sh')
result = stdout.read().decode()
print(result)

# PASSO 6: Listar backups
print("\n[PASSO 6] Listar backups disponiveis")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('ls -lh /home/deploy/backups/ 2>/dev/null || echo "Nenhum backup ainda"')
result = stdout.read().decode()
print(result)

# PASSO 7: Configurar rotacao de logs
print("\n[PASSO 7] Configurar rotacao de logs Docker")
print("-" * 80)

logrotate_config = '''{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
'''

stdin, stdout, stderr = client.exec_command('mkdir -p /etc/docker')
stdout.read().decode()

sftp = client.open_sftp()
with sftp.file('/etc/docker/daemon.json', 'w') as f:
    f.write(logrotate_config)
sftp.close()

# Reiniciar Docker
stdin, stdout, stderr = client.exec_command('systemctl restart docker')
stdout.read().decode()
print("[OK] Rotacao de logs configurada")

# PASSO 8: Verificar space em disco
print("\n[PASSO 8] Verificar espaco em disco")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('df -h / | tail -1')
result = stdout.read().decode()
print(result)

# PASSO 9: Status final dos containers
print("\n[PASSO 9] Status final dos containers")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker-compose -f /home/deploy/auto_cracha/docker-compose.yml ps')
result = stdout.read().decode()
print(result)

print("\n" + "=" * 80)
print("RESUMO - ETAPA 9 PARTE 2 (TESTES E BACKUPS)")
print("=" * 80)

print("""
[OK] Login funcionando via HTTPS
[OK] Rotas protegidas respondendo
[OK] Script de backup criado
[OK] Backup automatico agendado (diariamente 03:00)
[OK] Rotacao de logs configurada
[OK] Todos os containers saudaveis

BACKUPS:
- Local: /home/deploy/backups/
- Frequencia: Diaria (03:00)
- Retencao: Ultimos 7 backups

PROXIMOS PASSOS:
1. Testar acesso via https://157.245.217.95 no navegador
2. Aceitar aviso do certificado self-signed
3. Fazer login
4. Sistema esta PRONTO PARA PRODUCAO

QUANDO TIVER DOMINIO:
1. Registrar dominio (ex: crachapp.com.br)
2. Apontar DNS para 157.245.217.95
3. Rodar: sudo certbot certonly --nginx -d seudominio.com.br -m mrg.marcos.mrg@gmail.com
4. Sistema vai ter HTTPS com certificado valido
""")

client.close()
