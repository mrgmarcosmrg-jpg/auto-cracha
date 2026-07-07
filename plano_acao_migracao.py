import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("PLANO DE ACAO - APLICAR MIGRAÇÕES ALEMBIC")
print("=" * 80)

# PASSO 1: Verificar status das migrações
print("\n[PASSO 1] Verificar Status das Migrações")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose exec -T backend alembic current 2>&1')
output1 = stdout.read().decode()
print(output1)

# PASSO 2: Aplicar migrações
print("\n[PASSO 2] Aplicar Migrações (alembic upgrade head)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose exec -T backend alembic upgrade head 2>&1')
output2 = stdout.read().decode()
print(output2)

# PASSO 3: Reiniciar backend
print("\n[PASSO 3] Reiniciar Backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 10')
output3 = stdout.read().decode()
print("Backend reiniciado. Aguardando 10 segundos...")

# PASSO 4: Verificar health endpoint
print("\n[PASSO 4] Verificar Health Endpoint")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/health | python3 -m json.tool 2>&1 || curl -s http://localhost:8000/health')
output4 = stdout.read().decode()
print(output4)

# PASSO 5: Verificar estrutura da tabela usuarios
print("\n[PASSO 5] Verificar Estrutura da Tabela usuarios")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_postgres psql -U crachapp -d crachapp -c "\\d usuarios" 2>&1')
output5 = stdout.read().decode()
print(output5)

# PASSO 6: Rodar seed (se script existir)
print("\n[PASSO 6] Verificar e Rodar Seed (se existir)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('ls -la /home/deploy/auto_cracha/backend/seed.py 2>&1')
seed_check = stdout.read().decode()
print("Verificando seed.py:")
print(seed_check)

if "No such file" not in seed_check:
    print("\nExecutando seed.py...")
    stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose exec -T backend python backend/seed.py 2>&1')
    output6 = stdout.read().decode()
    print(output6[-1000:])  # Últimas 1000 chars
else:
    print("Arquivo seed.py não encontrado. Saltando este passo.")

# PASSO 7: Testar login
print("\n[PASSO 7] Testar Login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\' 2>&1')
output7 = stdout.read().decode()
print("Resposta do login (primeiros 500 chars):")
print(output7[:500])

if 'access_token' in output7:
    print("\n\n✓✓✓ SUCESSO! LOGIN FUNCIONANDO! ✓✓✓")
else:
    print("\n⚠ Resposta completa:")
    print(output7)

client.close()

print("\n" + "=" * 80)
print("FIM DO PLANO DE ACAO")
print("=" * 80)
