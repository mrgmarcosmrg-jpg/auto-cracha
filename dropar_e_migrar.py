import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("DELETAR TABELA INCOMPLETA E RODAR MIGRAÇÕES")
print("=" * 80)

# Deletar a tabela usuarios incompleta
print("\n[PASSO 1] Deletar tabela usuarios incompleta")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "DROP TABLE IF EXISTS usuarios CASCADE;"''')
print(stdout.read().decode())

# Rodar alembic upgrade head
print("\n[PASSO 2] Rodar alembic upgrade head (vai criar tabela com schema completo)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic upgrade head 2>&1')
output = stdout.read().decode()
print(output)

# Contar colunas na nova tabela
print("\n[PASSO 3] Verificar estrutura completa da tabela usuarios")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "\\d usuarios"''')
output = stdout.read().decode()
print(output)

# Contar total
print("\n[PASSO 4] Total de colunas")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT count(*) as total_colunas FROM information_schema.columns WHERE table_name = 'usuarios';"''')
print(stdout.read().decode())

# Reiniciar backend
print("\n[PASSO 5] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK]")

# Criar usuário admin
print("\n[PASSO 6] Inserir usuário admin")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true)
ON CONFLICT (email) DO NOTHING;

SELECT email, nome, perfil FROM usuarios;
SQL''')
print(stdout.read().decode())

# Testar login
print("\n[PASSO 7] Testar login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()

if 'access_token' in login_output:
    print("[SUCESSO!!!] LOGIN FUNCIONANDO!")
    print(login_output[:200])
else:
    print("[INFO]")
    print(login_output[:500])

client.close()

print("\n" + "=" * 80)
print("FIM")
print("=" * 80)
