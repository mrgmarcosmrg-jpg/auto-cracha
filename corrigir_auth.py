import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

# Criar novo schema com 'password' em vez de 'senha'
novo_schema = '''from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    nome_empresa: str
    cnpj: str
    email: EmailStr
    password: str = Field(min_length=8, alias="senha")
    nome_responsavel: str

    class Config:
        populate_by_name = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(alias="senha")

    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(min_length=8)


class AceitarConviteRequest(BaseModel):
    password: str = Field(min_length=8, alias="senha")

    class Config:
        populate_by_name = True
'''

# Enviar para o servidor
cmd = f"cat > /home/deploy/auto_cracha/backend/app/schemas/auth.py << 'EOF'\n{novo_schema}\nEOF"
stdin, stdout, stderr = client.exec_command(cmd)
print("Schema atualizado!")

# Agora corrigir o auth.py para usar 'password' em vez de 'senha'
stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/backend/app/routes/auth.py')
content = stdout.read().decode()

# Substituir payload.senha por payload.password
novo_auth = content.replace('payload.senha', 'payload.password')
novo_auth = novo_auth.replace('hash_password(payload.password)', 'hash_password(payload.password)')

# Enviar para o servidor
cmd = f"cat > /home/deploy/auto_cracha/backend/app/routes/auth.py << 'EOF'\n{novo_auth}\nEOF"
stdin, stdout, stderr = client.exec_command(cmd)
print("Auth.py atualizado!")

# Restart backend
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose restart backend')
print("Backend reiniciado!")

# Aguardar um pouco
import time
time.sleep(5)

# Testar login novamente
stdin, stdout, stderr = client.exec_command('''curl -s -X POST http://localhost:8000/auth/login \\
  -H "Content-Type: application/json" \\
  -H "Origin: http://157.245.217.95:3000" \\
  -d '{"email":"admin@crachapp.com.br","password":"Admin0123456"}' | python -m json.tool 2>/dev/null || echo "Erro no JSON"''')
output = stdout.read().decode()
print("\nResposta do login:")
print(output)

client.close()
