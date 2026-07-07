import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\n" + "=" * 80)
print("DIAGNOSTICO PROFUNDO - CSS E CONECTIVIDADE")
print("=" * 80)

# 1. Status dos containers
print("\n[1] Status dos containers")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker-compose -f /home/deploy/auto_cracha/docker-compose.yml ps')
print(stdout.read().decode())

# 2. Logs do frontend
print("\n[2] Logs do container frontend (ultimas 30 linhas)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker logs crachapp_frontend 2>&1 | tail -30')
logs = stdout.read().decode()
print(logs)

# 3. Verificar se .next foi gerado
print("\n[3] Verificar se pasta .next foi gerada")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend ls -la /app/.next/ | head -15')
result = stdout.read().decode()
print(result if result else "ERRO: .next nao existe!")

# 4. Verificar arquivo de login no container
print("\n[4] Verificar se arquivo page.tsx foi atualizado no container")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend head -20 /app/src/app/login/page.tsx')
content = stdout.read().decode()
if 'gradient-to-br from-blue-600' in content:
    print("[OK] Arquivo CONTÉM o novo CSS!")
    print(content[:300])
else:
    print("[ERRO] Arquivo NAO foi atualizado!")
    print(content[:300])

# 5. Verificar variavel de ambiente NEXT_PUBLIC_API_URL
print("\n[5] Verificar variaveis de ambiente do frontend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend env | grep -i "api\|next"')
env_vars = stdout.read().decode()
print(env_vars if env_vars else "(nenhuma variavel encontrada)")

# 6. Testar conectividade backend
print("\n[6] Testar conectividade ao backend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -k -s https://157.245.217.95:8000/health | head -c 200')
result = stdout.read().decode()
print("Resposta:", result)

# 7. Testar via localhost (dentro da rede docker)
print("\n[7] Testar backend dentro da rede docker")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend curl -s http://crachapp_backend:8000/health | head -c 200')
result = stdout.read().decode()
print("Resposta:", result)

# 8. Verificar Dockerfile
print("\n[8] Verificar Dockerfile (confirmar RUN rm -rf .next)")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/frontend-web/Dockerfile')
dockerfile = stdout.read().decode()
if 'rm -rf .next' in dockerfile:
    print("[OK] Dockerfile contém RUN rm -rf .next")
else:
    print("[ERRO] Dockerfile NAO contém RUN rm -rf .next")
print("\nConteudo do Dockerfile:")
print(dockerfile)

# 9. Verificar arquivo CSS compilado
print("\n[9] Verificar se CSS foi compilado")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend find /app/.next -name "*.css" 2>/dev/null | head -5')
result = stdout.read().decode()
print("CSS files encontrados:", result if result else "NENHUM!")

# 10. Acessar HTML da login page
print("\n[10] Acessar HTML completo da login page")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('curl -k -s https://157.245.217.95/login | head -100')
html = stdout.read().decode()
print("HTML primeiras 100 linhas:")
print(html[:800])

print("\n" + "=" * 80)
print("FIM DO DIAGNOSTICO")
print("=" * 80)

client.close()
