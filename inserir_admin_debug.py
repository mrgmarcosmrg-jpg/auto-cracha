import paramiko
import uuid

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("INSERIR ADMIN COM DEBUG")
print("=" * 80)

# Gerar um UUID para o admin
admin_id = str(uuid.uuid4())
print(f"\nAdmin ID: {admin_id}")

# Hash da senha "Admin0123456" em bcrypt
password_hash = '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e'

# INSERT com detalhes
insert_cmd = f'''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
INSERT INTO usuarios (
    id,
    email,
    nome,
    senha_hash,
    perfil,
    ativo
) VALUES (
    '{admin_id}',
    'admin@crachapp.com.br',
    'Administrador',
    '{password_hash}',
    'SUPER_ADMIN',
    true
);

SELECT email, nome, perfil, ativo FROM usuarios WHERE email = 'admin@crachapp.com.br';
SQL'''

print("\nExecutando INSERT:")
print("-" * 80)
stdin, stdout, stderr = client.exec_command(insert_cmd)
output = stdout.read().decode()
errors = stderr.read().decode()

if output:
    print("OUTPUT:")
    print(output)
if errors:
    print("ERRORS:")
    print(errors)

# Verificar se foi inserido
print("\nVerificando INSERT:")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT count(*) FROM usuarios WHERE email = 'admin@crachapp.com.br';"''')
count = stdout.read().decode()
print(f"Total de registros admin: {count}")

# Teste de login
print("\nTeste de login:")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
login_result = stdout.read().decode()
print(login_result[:400])

if 'access_token' in login_result:
    print("\nSUCESSO!!!!")
else:
    print("\nSem token")

client.close()
