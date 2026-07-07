import paramiko
import uuid

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 80)
print("INSERIR ADMIN DIRETAMENTE")
print("=" * 80)

admin_id = str(uuid.uuid4())
password_hash = '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e'

# Usar -c para executar comando direto no psql
print("\nPasso 1: Inserir usuario admin")
print("-" * 80)

cmd = f"""docker exec crachapp_postgres psql -U crachapp -d crachapp -c "INSERT INTO usuarios (id, email, nome, senha_hash, perfil, ativo) VALUES ('{admin_id}', 'admin@crachapp.com.br', 'Administrador', '{password_hash}', 'SUPER_ADMIN'::perfil_usuario, true);" """

stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode()
err = stderr.read().decode()

print("Output:", out if out else "(vazio)")
print("Error:", err if err else "(nenhum)")

# Verificar
print("\nPasso 2: Listar usuarios")
print("-" * 80)

stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT id, email, nome, perfil FROM usuarios;" ''')
result = stdout.read().decode()
print(result)

# Se ainda vazio, tentar uma sintaxe mais simples
if '(0 rows)' in result:
    print("\nAinda vazio! Tentando sintaxe alternativa...")
    print("-" * 80)

    # Sem tipos definidos
    cmd2 = f"""docker exec -it crachapp_postgres psql -U crachapp -d crachapp -c 'INSERT INTO usuarios (id, email, nome, senha_hash, perfil, ativo) VALUES ('\\'{admin_id}\\'' , '\\admin@crachapp.com.br\\'' , 'Administrador' , '\\{password_hash}\\' , \\'SUPER_ADMIN\\' , true);' """

    # Dessa vez deixa simples mesmo
    simple_cmd = '''docker exec crachapp_postgres bash -c "psql -U crachapp -d crachapp << 'EOSQL'
INSERT INTO usuarios (id, email, nome, senha_hash, perfil, ativo)
VALUES ('''' + admin_id + '''''', '''' + 'admin@crachapp.com.br' + '''''', '''Administrador''' , '''''' + password_hash + '''''''' , '''SUPER_ADMIN'''::perfil_usuario , true);
EOSQL
"'''

    stdin, stdout, stderr = client.exec_command(simple_cmd)
    out2 = stdout.read().decode()
    err2 = stderr.read().decode()

    print("Output:", out2 if out2 else "(vazio)")
    print("Error:", err2 if err2 else "(nenhum)")

# Teste final de login
print("\nPasso 3: Teste de login")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
login_result = stdout.read().decode()

if 'access_token' in login_result:
    print("[SUCESSO] LOGIN FUNCIONANDO!")
    print(login_result[:300])
else:
    print("[ERRO] Login falhou")
    print(login_result[:300])

client.close()
