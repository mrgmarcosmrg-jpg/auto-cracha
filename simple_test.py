import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Testando status dos containers...")
stdin, stdout, stderr = client.exec_command('docker ps | grep crachapp')
print(stdout.read().decode())

print("\nTestando health do backend...")
stdin, stdout, stderr = client.exec_command('curl -s -m 5 http://localhost:8000/health 2>&1 | head -c 200')
print(stdout.read().decode())

print("\n\nTestando login...")
stdin, stdout, stderr = client.exec_command('curl -s -m 5 -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\' 2>&1 | head -c 300')
print(stdout.read().decode())

client.close()
