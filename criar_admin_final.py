import paramiko
import uuid

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("CRIAR ADMIN - METODO COM ARQUIVO SQL")
print("=" * 80)

admin_id = str(uuid.uuid4())
password_hash = '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e'

# Conteudo do arquivo SQL
sql_content = f"""INSERT INTO usuarios (id, email, nome, senha_hash, perfil, ativo)
VALUES ('{admin_id}', 'admin@crachapp.com.br', 'Administrador', '{password_hash}', 'SUPER_ADMIN'::perfil_usuario, true);

SELECT email, nome, perfil, ativo FROM usuarios;
"""

print("\nSQL a ser executado:")
print("-" * 80)
print(sql_content)

# Criar arquivo SQL no servidor
print("\nCriando arquivo SQL no servidor...")
print("-" * 80)
sftp = client.open_sftp()
with sftp.file('/tmp/insert_admin.sql', 'w') as f:
    f.write(sql_content)
sftp.close()
print("[OK]")

# Executar o arquivo SQL
print("\nExecutando arquivo SQL...")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -f /tmp/insert_admin.sql''')
output = stdout.read().decode()
errors = stderr.read().decode()

print("OUTPUT:")
print(output)
if errors:
    print("ERRORS:")
    print(errors)

# Verificar
print("\nVerificando registros:")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT count(*) FROM usuarios;"''')
count = stdout.read().decode()
print(count)

# Testar login
print("\nTestando login...")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
result = stdout.read().decode()

if 'access_token' in result:
    print("[SUCESSO] Token gerado!")
    print(result[:200])
else:
    print("[ERRO]")
    print(result[:200])

client.close()
