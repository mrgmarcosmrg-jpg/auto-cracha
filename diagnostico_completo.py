import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("DIAGNOSTICO COMPLETO DO PROJETO")
print("=" * 80)

# 1. Estrutura de arquivos
print("\n1. ESTRUTURA DE ARQUIVOS\n")
stdin, stdout, stderr = client.exec_command('find /home/deploy/auto_cracha -type f -name "*.py" | grep -E "(models|schemas|routes)" | head -20')
print(stdout.read().decode())

# 2. Modelo Usuario
print("\n2. MODELO Usuario (models/usuario.py)\n")
stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/backend/app/models/usuario.py | head -80')
print(stdout.read().decode())

# 3. Estrutura da tabela no banco
print("\n3. ESTRUTURA DA TABELA usuarios NO BANCO\n")
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "\\d usuarios"''')
print(stdout.read().decode())

# 4. Migrations disponíveis
print("\n4. MIGRATIONS (alembic/versions/)\n")
stdin, stdout, stderr = client.exec_command('ls -la /home/deploy/auto_cracha/backend/alembic/versions/')
print(stdout.read().decode())

# 5. Primeira migration
print("\n5. CONTEUDO DA PRIMEIRA MIGRATION\n")
stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/backend/alembic/versions/0001_initial_schema.py | head -100')
print(stdout.read().decode())

# 6. Status dos containers
print("\n6. STATUS DOS CONTAINERS\n")
stdin, stdout, stderr = client.exec_command('docker ps -a --format "table {{.Names}}\t{{.Status}}"')
print(stdout.read().decode())

client.close()

print("\n" + "=" * 80)
print("FIM DO DIAGNOSTICO")
print("=" * 80)
