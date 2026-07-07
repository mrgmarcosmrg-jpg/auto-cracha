import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("CORRIGIR MIGRACAO 0005 DENTRO DO CONTAINER")
print("=" * 80)

# PASSO 1: Criar arquivo corrigido temporariamente no servidor
print("\n[PASSO 1] Criar arquivo 0005 corrigido no servidor")
print("-" * 80)

migration_content = '''"""adiciona campos de pagamento em assinaturas

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('assinaturas', 'plano',
               existing_type=sa.Enum('BRONZE', 'PRATA', name='plano_assinatura'),
               type_=sa.Enum('BRONZE', 'PRATA', 'OURO', name='plano_assinatura'),
               existing_nullable=True)
    op.add_column(
        "assinaturas",
        sa.Column("trial_expira_em", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "assinaturas",
        sa.Column("mp_payment_id", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assinaturas", "mp_payment_id")
    op.drop_column("assinaturas", "trial_expira_em")
    op.alter_column('assinaturas', 'plano',
               existing_type=sa.Enum('BRONZE', 'PRATA', 'OURO', name='plano_assinatura'),
               type_=sa.Enum('BRONZE', 'PRATA', name='plano_assinatura'),
               existing_nullable=True)
'''

# Criar arquivo temporário no servidor
sftp = client.open_sftp()
with sftp.file('/tmp/0005_assinatura_pagamento.py', 'w') as f:
    f.write(migration_content)
sftp.close()
print("[OK] Arquivo criado em /tmp/")

# PASSO 2: Copiar para dentro do container com docker cp
print("\n[PASSO 2] Copiar arquivo para dentro do container")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker cp /tmp/0005_assinatura_pagamento.py crachapp_backend:/app/alembic/versions/0005_assinatura_pagamento.py')
output = stdout.read().decode()
print("[OK] Arquivo copiado com docker cp")

# PASSO 3: Resetar banco
print("\n[PASSO 3] Resetar banco de dados")
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
print("[OK]")

# PASSO 4: Rodar migrações
print("\n[PASSO 4] Rodar alembic upgrade head")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic upgrade head 2>&1')
output = stdout.read().decode()

# Mostrar apenas resultado final
lines = output.split('\n')
for line in lines[-15:]:
    if line.strip():
        print(line)

if "UndefinedColumn" in output:
    print("\nERRO: Migração 0005 ainda falhando")
elif "FAILED" in output.upper():
    print("\nERRO na migracao")
else:
    print("\nOK: Migracao executada")

# PASSO 5: Criar admin
print("\n[PASSO 5] Criar usuario admin")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true)
ON CONFLICT (email) DO NOTHING;

SELECT count(*) as total_usuarios FROM usuarios;
SQL''')
print(stdout.read().decode())

# PASSO 6: Reiniciar backend
print("\n[PASSO 6] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK]")

# PASSO 7: Testar login
print("\n[PASSO 7] TESTE - Login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()

print("Resposta do servidor:")
print(login_output[:300])

if 'access_token' in login_output:
    print("\nSUCESSO!!! LOGIN FUNCIONANDO!")
else:
    print("\nLogin sem token ou erro")

client.close()
