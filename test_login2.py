import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 60)
print("TESTANDO LOGIN APOS CORRECAO")
print("=" * 60)

cmd = '''curl -i -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -H "Origin: http://157.245.217.95:3000" \\
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' 2>&1'''

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode())

print("\n" + "=" * 60)
print("VERIFICANDO LOGS")
print("=" * 60)

cmd2 = 'docker logs crachapp_backend --tail=30'
stdin, stdout, stderr = client.exec_command(cmd2)
print(stdout.read().decode())

client.close()
