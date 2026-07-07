import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("COPIAR alembic.ini E RODAR MIGRAÇÕES")
print("=" * 80)

# Copiar alembic.ini via SFTP
print("\n[PASSO 1] Copiar alembic.ini para o servidor via SFTP")
print("-" * 80)

try:
    sftp = client.open_sftp()
    sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/backend/alembic.ini',
             '/home/deploy/auto_cracha/backend/alembic.ini')
    sftp.close()
    print("[OK] alembic.ini copiado para /home/deploy/auto_cracha/backend/alembic.ini")
except Exception as e:
    print(f"[ERRO] Falha ao copiar: {e}")

# Verificar se arquivo está lá
print("\n[PASSO 2] Verificar se alembic.ini está no servidor")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('ls -la /home/deploy/auto_cracha/backend/alembic.ini')
print(stdout.read().decode())

# Rodar alembic current
print("\n[PASSO 3] Verificar status das migrações (alembic current)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha/backend && alembic current')
output = stdout.read().decode()
print(output)
stderr_output = stderr.read().decode()
if stderr_output:
    print("STDERR:", stderr_output)

# Rodar alembic upgrade head
print("\n[PASSO 4] Aplicar migrações (alembic upgrade head)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha/backend && alembic upgrade head')
output = stdout.read().decode()
print(output)
stderr_output = stderr.read().decode()
if stderr_output:
    print("STDERR:", stderr_output)

# Verificar estrutura da tabela
print("\n[PASSO 5] Verificar estrutura da tabela usuarios após migrações")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_postgres psql -U crachapp -d crachapp -c "\\d usuarios"')
print(stdout.read().decode())

# Reiniciar backend
print("\n[PASSO 6] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK] Backend reiniciado")

# Testar health
print("\n[PASSO 7] Testar health endpoint")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/health')
print(stdout.read().decode())

# Testar login
print("\n[PASSO 8] Testar login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()
print(login_output[:400])

if 'access_token' in login_output:
    print("\n[SUCESSO!!!] LOGIN FUNCIONANDO!")
else:
    print("\n[INFO] Resposta completa do login:")
    print(login_output)

client.close()
