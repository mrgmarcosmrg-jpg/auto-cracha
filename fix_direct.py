import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Corrigindo schema/auth.py com sed...")

# Alterar LoginRequest para aceitar 'password'
cmd1 = "sed -i 's/class LoginRequest/class LoginRequest_old/g' /home/deploy/auto_cracha/backend/app/schemas/auth.py"
stdin, stdout, stderr = client.exec_command(cmd1)

# Inserir nova definição antes de TokenResponse
cmd2 = '''sed -i '/^class TokenResponse/i class LoginRequest(BaseModel):\\n    email: EmailStr\\n    password: str\\n' /home/deploy/auto_cracha/backend/app/schemas/auth.py'''
stdin, stdout, stderr = client.exec_command(cmd2)

print("Schema alterado!")

# Alterar auth.py para usar payload.password
cmd3 = "sed -i 's/payload\\.senha/payload.password/g' /home/deploy/auto_cracha/backend/app/routes/auth.py"
stdin, stdout, stderr = client.exec_command(cmd3)

print("Auth.py alterado!")

# Reiniciar backend
cmd4 = "cd /home/deploy/auto_cracha && docker-compose restart backend && sleep 10"
stdin, stdout, stderr = client.exec_command(cmd4)
print("Backend reiniciado!")

# Testar login
cmd5 = '''curl -s -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}'  '''
stdin, stdout, stderr = client.exec_command(cmd5)
output = stdout.read().decode()
print("\nResposta do login:")
print(output[:500])

client.close()
