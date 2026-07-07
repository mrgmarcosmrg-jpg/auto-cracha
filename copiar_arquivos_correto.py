import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Copiando TODOS os arquivos .tsx melhorados para o servidor...")
print("=" * 80)

# Arquivos .tsx que foram modificados
arquivos = [
    'frontend-web/src/app/dashboard/page.tsx',
    'frontend-web/src/app/login/page.tsx',
    'frontend-web/src/app/register/page.tsx',
    'frontend-web/src/app/dashboard/colaboradores/page.tsx',
    'frontend-web/src/app/dashboard/lotes/page.tsx',
]

sftp = client.open_sftp()

for arquivo in arquivos:
    local_path = f'C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/{arquivo}'.replace('\\', '/')
    remote_path = f'/home/deploy/auto_cracha/{arquivo}'

    try:
        sftp.put(local_path, remote_path)
        print(f"[OK] {arquivo}")
    except Exception as e:
        print(f"[ERRO] {arquivo}: {e}")

sftp.close()

print("\n" + "=" * 80)
print("Arquivos copiados! Agora fazer rebuild...")
print("=" * 80)

# Rebuild
print("\nParando container...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose stop frontend')
stdout.read().decode()

print("Removendo container...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose rm -f frontend')
stdout.read().decode()

print("Removendo imagem...")
stdin, stdout, stderr = client.exec_command('docker image rm auto_cracha-frontend:latest 2>/dev/null || true')
stdout.read().decode()

print("Fazendo rebuild com --no-cache...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose build --no-cache frontend 2>&1')
output = stdout.read().decode()

# Mostrar linhas importantes
for line in output.split('\n')[-15:]:
    if line.strip() and ('Successfully' in line or 'Step' in line or 'error' in line.lower()):
        print(line)

print("\nIniciando container...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose up -d frontend && sleep 3')
stdout.read().decode()

# Verificar se arquivo foi copiado
print("\nVerificando se arquivo foi copiado corretamente...")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend grep -c "gradient-to-br" /app/src/app/login/page.tsx')
result = stdout.read().decode().strip()

if result == '1':
    print("[OK] ARQUIVO CONTEM O NOVO CSS!")
    print("\nAcesse agora: https://157.245.217.95/login")
    print("(Limpe cache do navegador com Ctrl+Shift+Delete se necessario)")
else:
    print("[ERRO] Arquivo AINDA NAO tem o novo CSS")
    print("Mostrando conteudo do arquivo no container:")
    stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend head -30 /app/src/app/login/page.tsx')
    print(stdout.read().decode())

client.close()
