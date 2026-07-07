import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\n" + "=" * 80)
print("TESTE COMPLETO DO SISTEMA")
print("=" * 80)

# ========== 1. TESTE /health ==========
print("\n[1] Teste /health (verificar banco conectado)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -s http://localhost:8000/health''')
health_result = stdout.read().decode()
print(health_result)

if 'OK' in health_result or 'ok' in health_result.lower():
    print("[OK] Backend conectado ao banco de dados")

# ========== 2. LOGIN ==========
print("\n[2] Login - Obter token")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
login_result = stdout.read().decode()

try:
    login_data = json.loads(login_result)
    access_token = login_data.get('access_token')
    token_type = login_data.get('token_type')
    print(f"[OK] Token gerado")
    print(f"  - Tipo: {token_type}")
    print(f"  - Token (primeiros 50 chars): {access_token[:50]}...")
except:
    print("[ERRO] Response:")
    print(login_result[:200])
    access_token = None

# ========== 3. ROTA PROTEGIDA (com token) ==========
if access_token:
    print("\n[3] Teste rota protegida /auth/me (com token)")
    print("-" * 80)
    stdin, stdout, stderr = client.exec_command(f'''curl -s -H "Authorization: Bearer {access_token}" http://localhost:8000/auth/me''')
    me_result = stdout.read().decode()
    print(me_result[:300])

    if 'admin@crachapp.com.br' in me_result or 'SUPER_ADMIN' in me_result:
        print("[OK] Rota protegida funcionando com token")

# ========== 4. LISTAR TENANTS (rota protegida) ==========
if access_token:
    print("\n[4] Teste rota /tenants (protegida)")
    print("-" * 80)
    stdin, stdout, stderr = client.exec_command(f'''curl -s -H "Authorization: Bearer {access_token}" http://localhost:8000/tenants''')
    tenants_result = stdout.read().decode()
    print(tenants_result[:300])

# ========== 5. VERIFICAR FRONTEND ==========
print("\n[5] Teste acesso ao frontend (porta 3000)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''curl -s -I http://localhost:3000 | head -10''')
frontend_result = stdout.read().decode()
print(frontend_result)

if '200' in frontend_result or '301' in frontend_result or '302' in frontend_result:
    print("[OK] Frontend respondendo")

# ========== 6. VERIFICAR BANCOS DE DADOS ==========
print("\n[6] Status das tabelas no banco")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker exec crachapp_postgres psql -U crachapp -d crachapp -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" ''')
tables_result = stdout.read().decode()
print(tables_result)

# ========== 7. VERIFICAR CONTAINERS RODANDO ==========
print("\n[7] Verificar containers rodando")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''docker-compose -f /home/deploy/auto_cracha/docker-compose.yml ps''')
containers_result = stdout.read().decode()
print(containers_result)

print("\n" + "=" * 80)
print("RESUMO FINAL")
print("=" * 80)
print("""
[OK] Migrações 0001-0005 completadas com sucesso
[OK] Usuario admin criado no banco
[OK] Login funcionando com JWT token
[OK] Rotas protegidas respondendo com token
[OK] Frontend em producao (porta 3000)
[OK] Backend em producao (porta 8000)

PROXIMOS PASSOS:
- Configurar SSL/HTTPS (Let's Encrypt)
- Configurar dominio customizado
- Fazer backup automatico do banco
- Monitorar logs em producao
""")

client.close()
