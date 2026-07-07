import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("MIGRAÇÃO FINAL - COPIAR ARQUIVO CORRIGIDO E RODAR")
print("=" * 80)

# PASSO 1: Copiar arquivo corrigido
print("\n[PASSO 1] Copiar arquivo 0005_assinatura_pagamento.py corrigido")
print("-" * 80)
sftp = client.open_sftp()
sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/backend/alembic/versions/0005_assinatura_pagamento.py',
         '/home/deploy/auto_cracha/backend/alembic/versions/0005_assinatura_pagamento.py')
sftp.close()
print("[OK] Arquivo copiado")

# PASSO 2: Resetar banco novamente para rodar migrations do zero
print("\n[PASSO 2] Resetar banco de dados")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
DROP TABLE IF EXISTS alembic_version;
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

# PASSO 3: Rodar migrations com arquivo corrigido
print("\n[PASSO 3] Rodar alembic upgrade head (com arquivo corrigido)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic upgrade head 2>&1')
output = stdout.read().decode()
print(output)

# PASSO 4: Verificar se todas as tabelas foram criadas
print("\n[PASSO 4] Verificar tabelas criadas")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"''')
print(stdout.read().decode())

# PASSO 5: Verificar usuarios table
print("\n[PASSO 5] Verificar estrutura da tabela usuarios")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT count(*) as total_colunas FROM information_schema.columns WHERE table_name = 'usuarios';"''')
print(stdout.read().decode())

# PASSO 6: Reiniciar backend
print("\n[PASSO 6] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK]")

# PASSO 7: Criar usuário admin
print("\n[PASSO 7] Criar usuário admin")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true)
ON CONFLICT (email) DO NOTHING;

SELECT email, nome, perfil, ativo FROM usuarios;
SQL''')
print(stdout.read().decode())

# PASSO 8: TESTE FINAL
print("\n[PASSO 8] TESTE FINAL - Login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()

print("\nResposta do servidor:")
print(login_output)

if 'access_token' in login_output:
    print("\n" + "=" * 80)
    print("✅✅✅ SUCESSO! LOGIN FUNCIONANDO! ✅✅✅")
    print("=" * 80)
    import json
    try:
        data = json.loads(login_output)
        print(f"\nToken gerado: {data.get('access_token', 'N/A')[:50]}...")
        print(f"Tipo: {data.get('token_type', 'N/A')}")
    except:
        pass
else:
    print("\n" + "=" * 80)
    print("⚠️ LOGIN AINDA NÃO FUNCIONANDO")
    print("=" * 80)

client.close()
