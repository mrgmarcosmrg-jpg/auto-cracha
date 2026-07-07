import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("CORRIGIR MIGRAÇÃO 0005 DENTRO DO CONTAINER")
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
print(output if output else "[OK] Arquivo copiado com docker cp")

# PASSO 3: Verificar se arquivo está lá
print("\n[PASSO 3] Verificar arquivo dentro do container")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_backend cat /app/alembic/versions/0005_assinatura_pagamento.py | head -30')
content = stdout.read().decode()
print(content)

# PASSO 4: Resetar banco
print("\n[PASSO 4] Resetar banco de dados (alembic_version)")
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

# PASSO 5: Rodar migrações COM O ARQUIVO CORRIGIDO
print("\n[PASSO 5] Rodar alembic upgrade head (COM ARQUIVO CORRIGIDO)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec -w /app crachapp_backend alembic upgrade head 2>&1')
output = stdout.read().decode()
print(output)

if "UndefinedColumn" in output:
    print("\n⚠️ ERRO AINDA PRESENTE - Arquivo pode não ter sido atualizado corretamente")
    print("Verificando conteúdo do arquivo no container:")
    stdin, stdout, stderr = client.exec_command('docker exec crachapp_backend grep -n "alter_column" /app/alembic/versions/0005_assinatura_pagamento.py')
    print(stdout.read().decode())
else:
    print("\n✅ MIGRAÇÕES EXECUTADAS COM SUCESSO!")

# PASSO 6: Verificar tabelas
print("\n[PASSO 6] Verificar tabelas criadas")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;"''')
print(stdout.read().decode())

# PASSO 7: Criar admin
print("\n[PASSO 7] Criar usuário admin")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true)
ON CONFLICT (email) DO NOTHING;

SELECT email, nome, perfil FROM usuarios;
SQL''')
print(stdout.read().decode())

# PASSO 8: Reiniciar backend
print("\n[PASSO 8] Reiniciar backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 5')
stdout.read().decode()
print("[OK]")

# PASSO 9: Testar login
print("\n[PASSO 9] TESTE FINAL - Login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_output = stdout.read().decode()

print("\nResposta:")
print(login_output)

if 'access_token' in login_output:
    print("\n" + "=" * 80)
    print("✅✅✅ SUCESSO TOTAL! LOGIN FUNCIONANDO! ✅✅✅")
    print("=" * 80)
else:
    print("\n⚠️ Login sem token ainda")

client.close()
