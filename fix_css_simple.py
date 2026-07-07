import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Copiando Dockerfile corrigido...")
sftp = client.open_sftp()
sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/frontend-web/Dockerfile'.replace('\\', '/'),
         '/home/deploy/auto_cracha/frontend-web/Dockerfile')
sftp.close()
print("[OK]")

print("Parando container...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose stop frontend')
stdout.read().decode()

print("Removendo container...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose rm -f frontend')
stdout.read().decode()

print("Removendo imagem...")
stdin, stdout, stderr = client.exec_command('docker image rm auto_cracha-frontend:latest 2>/dev/null || true')
stdout.read().decode()

print("Limpando cache...")
stdin, stdout, stderr = client.exec_command('docker builder prune -f 2>/dev/null || true')
stdout.read().decode()

print("REBUILD em andamento (2-3 minutos)...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose build --no-cache frontend 2>&1')
output = stdout.read().decode()
# Mostrar apenas linhas importantes
for line in output.split('\n')[-20:]:
    if line.strip():
        print(line)

print("Iniciando container...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose up -d frontend && sleep 3')
stdout.read().decode()

print("Verificando status...")
stdin, stdout, stderr = client.exec_command('docker-compose -f /home/deploy/auto_cracha/docker-compose.yml ps')
result = stdout.read().decode()
print(result)

print("\nPRONTO! Acesse: https://157.245.217.95/login")
print("(Limpe o cache do navegador se necessario: Ctrl+Shift+Delete)")

client.close()
