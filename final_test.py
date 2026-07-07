import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Aguardando backend ficar pronto...")
time.sleep(5)

print("\n=== TESTE 1: /health ===")
stdin, stdout, stderr = client.exec_command('curl -s http://localhost:8000/health | python -m json.tool 2>&1 | head -20')
print(stdout.read().decode())

print("\n=== TESTE 2: POST /auth/login ===")
stdin, stdout, stderr = client.exec_command('curl -s -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
out = stdout.read().decode()
print(out)

if 'access_token' in out:
    print("\n[SUCESSO!!] Login funcionando!")
else:
    print("\nDebugando...")
    stdin, stdout, stderr = client.exec_command('docker logs crachapp_backend | tail -20')
    print(stdout.read().decode())

client.close()
