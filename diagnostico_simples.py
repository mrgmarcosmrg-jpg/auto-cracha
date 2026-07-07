import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

# 1. Verificar se arquivo foi atualizado no container
print("\n[1] Arquivo page.tsx tem o novo CSS?")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend grep -c "gradient-to-br from-blue-600" /app/src/app/login/page.tsx')
result = stdout.read().decode().strip()
print("Resultado:", result)

# 2. Verificar se .next foi criado
print("\n[2] Pasta .next existe?")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend test -d /app/.next && echo "SIM" || echo "NAO"')
result = stdout.read().decode().strip()
print("Resultado:", result)

# 3. Verificar se CSS foi compilado
print("\n[3] Arquivos CSS compilados?")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend find /app/.next -name "*.css" -type f 2>/dev/null | wc -l')
result = stdout.read().decode().strip()
print("Numero de arquivos CSS:", result)

# 4. Testar backend
print("\n[4] Backend respondendo?")
stdin, stdout, stderr = client.exec_command('curl -k -s http://localhost:8000/health | grep -c "status"')
result = stdout.read().decode().strip()
print("Resposta (tem 'status'?):", result)

# 5. Testar frontend HTML
print("\n[5] HTML da login tem CrachApp?")
stdin, stdout, stderr = client.exec_command('curl -k -s https://localhost/login 2>/dev/null | grep -c "CrachApp"')
result = stdout.read().decode().strip()
print("Resultado:", result)

# 6. Dockerfile tem rm -rf .next?
print("\n[6] Dockerfile esta correto?")
stdin, stdout, stderr = client.exec_command('grep -c "rm -rf .next" /home/deploy/auto_cracha/frontend-web/Dockerfile')
result = stdout.read().decode().strip()
print("Tem 'rm -rf .next'?:", result)

# 7. Ver ultimas linhas do Dockerfile
print("\n[7] Ultimas linhas do Dockerfile:")
stdin, stdout, stderr = client.exec_command('tail -10 /home/deploy/auto_cracha/frontend-web/Dockerfile')
print(stdout.read().decode())

# 8. Testar se consegue executar npm run build
print("\n[8] Verificar node_modules instalado?")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend test -d /app/node_modules && echo "SIM" || echo "NAO"')
result = stdout.read().decode().strip()
print("Resultado:", result)

client.close()

print("\n" + "=" * 80)
print("FIM DO DIAGNOSTICO")
print("=" * 80)
