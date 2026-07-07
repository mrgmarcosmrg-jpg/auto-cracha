import paramiko
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 60)
print("TESTANDO POST /auth/login")
print("=" * 60)

cmd = '''curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: http://157.245.217.95:3000" \
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' 2>&1'''

stdin, stdout, stderr = client.exec_command(cmd)
output = stdout.read().decode()
print(output)

print("\n" + "=" * 60)
print("VERIFICANDO LOGS MAIS RECENTES")
print("=" * 60)

cmd2 = 'docker logs crachapp_backend | tail -50'
stdin, stdout, stderr = client.exec_command(cmd2)
output2 = stdout.read().decode()
print(output2)

client.close()
