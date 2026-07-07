import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Copiando register.page.tsx melhorado...")
sftp = client.open_sftp()
sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/frontend-web/src/app/register/page.tsx'.replace('\\', '/'),
         '/home/deploy/auto_cracha/frontend-web/src/app/register/page.tsx')
sftp.close()
print("[OK]")

print("Reconstruindo frontend...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose build --no-cache frontend 2>&1 | tail -5')
print(stdout.read().decode())

print("Reiniciando...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart frontend && sleep 2')
stdout.read().decode()

print("Testando...")
stdin, stdout, stderr = client.exec_command('curl -k -s https://157.245.217.95/register | head -10')
result = stdout.read().decode()
if '<!DOCTYPE' in result:
    print("[OK] Pronto!")
else:
    print(result[:200])

client.close()
