import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("RESET TOTAL DO BANCO E RODAR MIGRAÇÕES")
print("=" * 80)

# Resetar alembic
print("\n[PASSO 1] Resetar histórico do Alembic")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "DROP TABLE IF EXISTS alembic_version;"''')
print(stdout.read().decode())

# Deletar todas as tabelas
print("\n[PASSO 2] Deletar todas as tabelas")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
DROP TABLE IF EXISTS consentimentos_lgpd CASCADE;
DROP TABLE IF EXISTS lotes CASCADE;
DROP TABLE IF EXISTS crachás CASCADE;
DROP TABLE IF EXISTS colaboradores CASCADE;
DROP TABLE IF EXISTS assinaturas CASCADE;
DROP TABLE IF EXISTS config_empresas CASCADE;
DROP TABLE IF EXISTS usuarios CASCADE;
DROP TABLE IF EXISTS filiais CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;
DROP TYPE IF EXISTS status_colaborador;
DROP TYPE IF EXISTS status_tenant;
DROP TYPE IF EXISTS perfil_usuario;
DROP TYPE IF EXISTS plano_assinatura;
SQL''')
print(stdout.read().decode())

# Rodar alembic upgrade head
print("\n[PASSO 3] Rodar alembic upgrade head")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic upgrade head 2>&1 | tail -50')
print(stdout.read().decode())

# Contar tabelas criadas
print("\n[PASSO 4] Listar tabelas criadas")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"''')
print(stdout.read().decode())

# Contar colunas em usuarios
print("\n[PASSO 5] Estrutura completa da tabela usuarios")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "\\d usuarios"''')
print(stdout.read().decode())

# Reiniciar backend
print("\n[PASSO 6] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK]")

# Criar usuário admin
print("\n[PASSO 7] Inserir usuário admin")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true)
ON CONFLICT (email) DO NOTHING;

SELECT email, nome, perfil, ativo FROM usuarios;
SQL''')
print(stdout.read().decode())

# Testar login
print("\n[PASSO 8] TESTE FINAL - Login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()

if 'access_token' in login_output:
    print("[SUCESSO!!!] LOGIN FUNCIONANDO!")
    import json
    try:
        data = json.loads(login_output)
        print(f"Token tipo: {data.get('token_type', 'N/A')}")
        print(f"Acesso token criado: SIM")
    except:
        print(login_output[:200])
else:
    print("[Status:]")
    print(login_output[:300])

client.close()

print("\n" + "=" * 80)
print("FIM DO RESET E MIGRACAO")
print("=" * 80)
