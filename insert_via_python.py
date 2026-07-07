import paramiko
import uuid

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("INSERIR ADMIN VIA SCRIPT PYTHON NO CONTAINER")
print("=" * 80)

admin_id = str(uuid.uuid4())
password_hash = '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e'

# Script Python que vai rodar no container
py_script = f'''
import psycopg2
import uuid

conn = psycopg2.connect("dbname=crachapp user=crachapp host=postgres password=crachapp_senha_123456")
cursor = conn.cursor()

admin_id = "{admin_id}"
email = "admin@crachapp.com.br"
nome = "Administrador"
senha_hash = "{password_hash}"
perfil = "SUPER_ADMIN"
ativo = True

try:
    cursor.execute("""
        INSERT INTO usuarios (id, email, nome, senha_hash, perfil, ativo)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (admin_id, email, nome, senha_hash, perfil, ativo))

    conn.commit()

    cursor.execute("SELECT count(*) FROM usuarios")
    count = cursor.fetchone()[0]
    print(f"Usuarios no banco: {{count}}")

except Exception as e:
    print(f"Erro: {{e}}")
finally:
    cursor.close()
    conn.close()
'''

print("\nScript Python:")
print("-" * 80)
print(py_script)

# Copiar script para container
print("\nCopiando script para container...")
print("-" * 80)

sftp = client.open_sftp()
with sftp.file('/tmp/insert_admin.py', 'w') as f:
    f.write(py_script)
sftp.close()

# Copiar para dentro do container
stdin, stdout, stderr = client.exec_command('docker cp /tmp/insert_admin.py crachapp_backend:/tmp/insert_admin.py')
stdout.read().decode()
print("[OK]")

# Executar script Python no container
print("\nExecutando script no container...")
print("-" * 80)

stdin, stdout, stderr = client.exec_command('docker exec crachapp_backend python /tmp/insert_admin.py')
result = stdout.read().decode()
error = stderr.read().decode()

print("Resultado:")
print(result)
if error:
    print("Erro:")
    print(error)

# Teste de login
print("\nTestando login...")
print("-" * 80)

stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
login_result = stdout.read().decode()

if 'access_token' in login_result:
    print("[SUCESSO!] LOGIN FUNCIONANDO!")
    print(login_result[:200])
else:
    print("[ERRO]")
    print(login_result[:200])

client.close()
