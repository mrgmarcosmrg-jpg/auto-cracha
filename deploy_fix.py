import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=" * 60)
print("COPIANDO ARQUIVOS CORRIGIDOS")
print("=" * 60)

# Copiar auth.py
sftp = client.open_sftp()
sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/backend/app/schemas/auth.py',
         '/home/deploy/auto_cracha/backend/app/schemas/auth.py')
print("[OK] auth.py (schema) copiado")

sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/backend/app/routes/auth.py',
         '/home/deploy/auto_cracha/backend/app/routes/auth.py')
print("[OK] auth.py (routes) copiado")

sftp.close()

print("\n" + "=" * 60)
print("REBUILDING BACKEND")
print("=" * 60)

stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose build --no-cache backend')
output = stdout.read().decode()
if 'Successfully built' in output or 'Successfully tagged' in output:
    print("[OK] Backend rebuilt com sucesso")
else:
    print("[AVISO] Output do build:")
    print(output[-500:])

print("\n" + "=" * 60)
print("REINICIANDO BACKEND")
print("=" * 60)

stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose up -d backend && sleep 10')
stdin, stdout, stderr = client.exec_command('docker ps -a | grep backend')
print(stdout.read().decode())

print("\n" + "=" * 60)
print("TESTANDO LOGIN")
print("=" * 60)

stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' ''')
output = stdout.read().decode()
print(output[:500])

if 'access_token' in output:
    print("\n[SUCESSO!] LOGIN FUNCIONANDO!")
elif 'E-mail ou senha' in output:
    print("\n[ERRO] Falha de autenticacao")
else:
    print("\n[INFO] Resposta:")
    print(output)

client.close()
