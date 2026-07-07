import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Copiando arquivos de forma ROBUSTA...")
print("=" * 80)

# Diretorio local base
base_local = r'C:\Users\GC-ACERECOM-G-E-F\Desktop\auto cracha\auto_cracha'

# Arquivos a copiar com seus caminhos
arquivos = [
    ('frontend-web/src/app/dashboard/page.tsx', '/home/deploy/auto_cracha/frontend-web/src/app/dashboard/page.tsx'),
    ('frontend-web/src/app/login/page.tsx', '/home/deploy/auto_cracha/frontend-web/src/app/login/page.tsx'),
    ('frontend-web/src/app/register/page.tsx', '/home/deploy/auto_cracha/frontend-web/src/app/register/page.tsx'),
    ('frontend-web/src/app/dashboard/colaboradores/page.tsx', '/home/deploy/auto_cracha/frontend-web/src/app/dashboard/colaboradores/page.tsx'),
    ('frontend-web/src/app/dashboard/lotes/page.tsx', '/home/deploy/auto_cracha/frontend-web/src/app/dashboard/lotes/page.tsx'),
]

sftp = client.open_sftp()

for rel_path, remote_path in arquivos:
    local_file = os.path.join(base_local, rel_path)

    print(f"\n[{rel_path}]")
    print(f"  Local: {local_file}")
    print(f"  Remote: {remote_path}")

    # Verificar se arquivo local existe
    if not os.path.exists(local_file):
        print(f"  [ERRO] Arquivo local nao existe!")
        continue

    # Ler conteudo do arquivo local
    try:
        with open(local_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"  [OK] Arquivo local lido ({len(content)} bytes)")
    except Exception as e:
        print(f"  [ERRO] Nao conseguiu ler: {e}")
        continue

    # Verificar se tem novo CSS
    if 'gradient-to-br' in content or 'from-blue-600' in content:
        print(f"  [OK] Contem novo CSS/Tailwind!")
    else:
        print(f"  [AVISO] Nao tem novo CSS - pode estar versao antiga")

    # Copiar para servidor
    try:
        sftp.putfo(open(local_file, 'rb'), remote_path)
        print(f"  [OK] Copiado para servidor!")
    except Exception as e:
        print(f"  [ERRO] Nao conseguiu copiar: {e}")

sftp.close()

print("\n" + "=" * 80)
print("Arquivos copiados! Fazendo rebuild...")
print("=" * 80)

# Rebuild
print("\nParando...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose stop frontend')
stdout.read().decode()

print("Removendo...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose rm -f frontend')
stdout.read().decode()

print("Removendo imagem...")
stdin, stdout, stderr = client.exec_command('docker image rm auto_cracha-frontend:latest 2>/dev/null || true')
stdout.read().decode()

print("Rebuild (pode levar 2-3 minutos)...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose build --no-cache frontend 2>&1')
output = stdout.read().decode()
for line in output.split('\n')[-10:]:
    if 'Successfully' in line or 'error' in line.lower():
        print(line)

print("Iniciando...")
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose up -d frontend && sleep 3')
stdout.read().decode()

# Verificacao final
print("\nVerificando...")
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend grep -c "gradient-to-br from-blue" /app/src/app/login/page.tsx 2>/dev/null')
result = stdout.read().decode().strip()

if result == '1':
    print("\n[SUCESSO!!] ARQUIVO TEM O NOVO CSS NO CONTAINER!")
    print("\nAcesse: https://157.245.217.95/login")
    print("Limpe cache: Ctrl+Shift+Delete")
else:
    print(f"\n[INFO] Resultado: {result}")
    print("Se ainda nao aparecer, tente em modo incognito/anonimo")

client.close()
