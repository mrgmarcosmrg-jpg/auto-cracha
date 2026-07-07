import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=== Status de TODOS os containers ===")
stdin, stdout, stderr = client.exec_command('docker ps -a')
print(stdout.read().decode())

print("\n=== Logs do backend ===")
stdin, stdout, stderr = client.exec_command('docker logs crachapp_backend 2>&1 | tail -50')
print(stdout.read().decode())

print("\n=== Tentando iniciar backend ===")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose up -d backend')
print(stdout.read().decode())

print("\n=== Aguardando 5 segundos ===")
import time
time.sleep(5)

print("\n=== Status novamente ===")
stdin, stdout, stderr = client.exec_command('docker ps | grep backend')
print(stdout.read().decode())

client.close()
