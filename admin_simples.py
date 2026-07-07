import paramiko
import uuid

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("INSERIR ADMIN - METODO SIMPLES")
print("=" * 80)

admin_id = str(uuid.uuid4())
password_hash = '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e'

# Usar comando via bash com heredoc
cmd = f'''docker exec crachapp_postgres bash -c 'psql -U crachapp -d crachapp << ENDOFSQL
INSERT INTO usuarios (id, email, nome, senha_hash, perfil, ativo)
VALUES (\\'{admin_id}\\' , \\'admin@crachapp.com.br\\' , \\'Administrador\\' , \\'{password_hash}\\' , \\'SUPER_ADMIN\\'::perfil_usuario , true);

SELECT count(*) as total FROM usuarios;
ENDOFSQL
' '''

print("\nExecutando INSERT...")
print("-" * 80)

stdin, stdout, stderr = client.exec_command(cmd)
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

print("Resposta:")
if 'access_token' in login_result:
    print("[SUCESSO!] LOGIN FUNCIONANDO!")
    import json
    try:
        data = json.loads(login_result)
        print(f"Token type: {data.get('token_type')}")
        print(f"Token: {str(data.get('access_token'))[:50]}...")
    except:
        print(login_result[:200])
else:
    print("[ERRO]")
    print(login_result[:200])

client.close()
