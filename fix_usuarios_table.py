import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Deletando e recriando tabela usuarios com estrutura completa...")

cmd = '''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
DROP TABLE IF EXISTS usuarios CASCADE;

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID,
    filial_id UUID,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    perfil VARCHAR(50) DEFAULT 'VISUALIZADOR',
    ativo BOOLEAN DEFAULT true,
    convite_token VARCHAR(255),
    convite_expira_em TIMESTAMP,
    reset_token VARCHAR(255),
    reset_token_expira_em TIMESTAMP,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true);

SELECT email, nome, perfil FROM usuarios;
SQL'''

stdin, stdout, stderr = client.exec_command(cmd)
output = stdout.read().decode()
print(output)

print("\nTestando login novamente...")
import time
time.sleep(2)

stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_response = stdout.read().decode()
print(login_response[:300])

if 'access_token' in login_response:
    print("\n\nSUCESSO!!! LOGIN FUNCIONANDO!!!")
else:
    print("\nResposta do login acima")

client.close()
