import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Verificando se arquivo foi realmente copiado no servidor...")
print("=" * 80)

# 1. Ver arquivo no servidor (host)
print("\n[1] Arquivo no SERVIDOR (host)?")
stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/frontend-web/src/app/login/page.tsx | head -20')
result = stdout.read().decode()
if 'gradient-to-br' in result:
    print("[OK] Arquivo NO SERVIDOR tem o novo CSS!")
else:
    print("[ERRO] Arquivo NO SERVIDOR nao tem o novo CSS")
print("\nPrimeiras 20 linhas:")
print(result)

# 2. Ver arquivo no container
print("\n[2] Arquivo no CONTAINER?")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend cat /app/src/app/login/page.tsx 2>/dev/null | head -20')
result = stdout.read().decode()
if 'gradient-to-br' in result:
    print("[OK] Arquivo NO CONTAINER tem o novo CSS!")
else:
    print("[ERRO] Arquivo NO CONTAINER nao tem o novo CSS")
print("\nPrimeiras 20 linhas:")
print(result[:500] if result else "(vazio ou erro)")

# 3. Ver o Dockerfile para entender como copia
print("\n[3] Dockerfile (como copia os arquivos)?")
stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/frontend-web/Dockerfile | grep -A5 "COPY"')
result = stdout.read().decode()
print(result)

client.close()
