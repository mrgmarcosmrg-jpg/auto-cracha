import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("RODAR ALEMBIC DENTRO DO CONTAINER")
print("=" * 80)

# Copiar alembic.ini para dentro do container
print("\n[PASSO 1] Copiar alembic.ini para dentro do container")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker cp /home/deploy/auto_cracha/backend/alembic.ini crachapp_backend:/app/alembic.ini')
stdout.read().decode()
print("[OK] alembic.ini copiado para o container")

# Verificar alembic current no container
print("\n[PASSO 2] Verificar status (alembic current dentro do container)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic current 2>&1')
output = stdout.read().decode()
print(output)

# Rodar alembic upgrade head no container
print("\n[PASSO 3] Aplicar migrações (alembic upgrade head no container)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic upgrade head 2>&1')
output = stdout.read().decode()
print(output)

# Verificar estrutura da tabela
print("\n[PASSO 4] Estrutura da tabela usuarios após migrações")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \'usuarios\' ORDER BY ordinal_position;"')
print(stdout.read().decode())

# Contar colunas
print("\n[PASSO 5] Contar total de colunas")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT count(*) FROM information_schema.columns WHERE table_name = \'usuarios\';"')
print(stdout.read().decode())

# Reiniciar backend
print("\n[PASSO 6] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK] Backend reiniciado")

# Testar login
print("\n[PASSO 7] Testar login POST /auth/login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()

if 'access_token' in login_output:
    print("[SUCESSO!!!] Login funcionando!")
    # Extrair token
    import json
    try:
        data = json.loads(login_output)
        print(f"Token: {data.get('access_token', 'N/A')[:50]}...")
    except:
        print(login_output)
elif 'tenant_id' in login_output and 'does not exist' in login_output:
    print("[PROBLEMA] Ainda há erro de coluna ausente")
    print(login_output[:300])
else:
    print("[INFO] Output completo:")
    print(login_output)

client.close()

print("\n" + "=" * 80)
print("FIM")
print("=" * 80)
