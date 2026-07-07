import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\n" + "=" * 80)
print("VERIFICAR STATUS DO ADMIN")
print("=" * 80)

# Verificar se a tabela usuarios tem dados
print("\n[1] Verificar dados da tabela usuarios")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT id, email, nome, perfil FROM usuarios;"''')
usuarios_result = stdout.read().decode()
print(usuarios_result)

# Verificar estrutura da tabela
print("\n[2] Estrutura da tabela usuarios")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "\\d usuarios"''')
estrutura = stdout.read().decode()
print(estrutura)

# Inserir admin se nao existir
print("\n[3] INSERIR admin de novo (forcar)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp << 'SQL'
DELETE FROM usuarios WHERE email = 'admin@crachapp.com.br';

INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', '$2b$12$Ft74tPqybqu9DDP2qTr21OQcBlWl0FfZCsOy2CNR01HcOPVo2or8e', 'SUPER_ADMIN', true);

SELECT email, nome, perfil, ativo FROM usuarios;
SQL''')
print(stdout.read().decode())

# Testar login de novo
print("\n[4] TESTE LOGIN")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
login_result = stdout.read().decode()
print("Resposta completa:")
print(login_result)

if 'access_token' in login_result:
    print("\n[SUCESSO] Token gerado!")
    import json
    try:
        data = json.loads(login_result)
        print(f"Token tipo: {data.get('token_type', 'N/A')}")
    except:
        pass
else:
    print("\n[ERRO] Sem token ainda")

client.close()
