import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Aguardando backend inicializar completamente...")
time.sleep(10)

print("\n=== TESTE: POST /auth/login ===")
stdin, stdout, stderr = client.exec_command('curl -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d \'{"email":"admin@crachapp.com.br","password":"Admin0123456"}\'')
output = stdout.read().decode()
print(output)

if 'access_token' in output:
    print("\n\nSUCESSO!!! LOGIN FUNCIONANDO!!!")
elif '422' in output:
    print("\nAinda tem erro de validacao")
else:
    print("\nOutput completo recebido acima")

client.close()
