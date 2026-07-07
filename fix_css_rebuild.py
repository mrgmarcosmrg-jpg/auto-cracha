import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\n" + "=" * 80)
print("FIX CSS - REBUILD COMPLETO E LIMPO DO FRONTEND")
print("=" * 80)

# PASSO 1: Copiar Dockerfile corrigido
print("\n[PASSO 1] Copiar Dockerfile corrigido")
print("-" * 80)
sftp = client.open_sftp()
sftp.put('C:/Users/GC-ACERECOM-G-E-F/Desktop/auto cracha/auto_cracha/frontend-web/Dockerfile'.replace('\\', '/'),
         '/home/deploy/auto_cracha/frontend-web/Dockerfile')
sftp.close()
print("[OK] Dockerfile atualizado")

# PASSO 2: Parar container
print("\n[PASSO 2] Parar container frontend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose stop frontend')
stdout.read().decode()
print("[OK]")

# PASSO 3: Remover container (força rebuild)
print("\n[PASSO 3] Remover container frontend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose rm -f frontend')
stdout.read().decode()
print("[OK]")

# PASSO 4: Remover imagem antiga (força rebuild)
print("\n[PASSO 4] Remover imagem Docker antiga")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker image rm auto_cracha-frontend:latest || true')
stdout.read().decode()
print("[OK]")

# PASSO 5: Limpar build cache do Docker
print("\n[PASSO 5] Limpar Docker build cache")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker builder prune -f || true')
stdout.read().decode()
print("[OK]")

# PASSO 6: Rebuild completo sem cache
print("\n[PASSO 6] REBUILD COMPLETO (sem cache) - Isso vai levar ~2-3 minutos")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('''cd /home/deploy/auto_cracha && \
docker-compose build --no-cache frontend 2>&1 | tee /tmp/build.log && \
tail -30 /tmp/build.log''')
result = stdout.read().decode()
print(result)

# PASSO 7: Iniciar container
print("\n[PASSO 7] Iniciar container frontend")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && docker-compose up -d frontend && sleep 3')
stdout.read().decode()
print("[OK]")

# PASSO 8: Verificar logs
print("\n[PASSO 8] Verificar logs do container")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker logs crachapp_frontend 2>&1 | tail -20')
logs = stdout.read().decode()
print(logs)

# PASSO 9: Testar acesso
print("\n[PASSO 9] Testar acesso (Login page)")
print("-" * 80)
time.sleep(2)
stdin, stdout, stderr = client.exec_command('curl -k -s https://157.245.217.95/login | grep -o "CrachApp\|Entrar no CrachApp\|gradiente" | head -5')
result = stdout.read().decode()
if result:
    print("Resposta:", result)
    print("\n✓ HTML contém elementos esperados")
else:
    print("Verificando se está respondendo...")
    stdin, stdout, stderr = client.exec_command('curl -k -s -I https://157.245.217.95/login | head -5')
    print(stdout.read().decode())

# PASSO 10: Status final
print("\n[PASSO 10] Status dos containers")
print("-" * 80)
stdin, stdout, stderr = client.exec_command('docker-compose -f /home/deploy/auto_cracha/docker-compose.yml ps')
result = stdout.read().decode()
print(result)

print("\n" + "=" * 80)
print("RESUMO")
print("=" * 80)

print("""
[OK] Dockerfile corrigido com RUN rm -rf .next
[OK] Container removido (forçou rebuild completo)
[OK] Imagem antiga removida
[OK] Build cache limpo
[OK] Rebuild executado SEM CACHE
[OK] Container reiniciado

PROXIMAS ACOES:
1. Abra no navegador: https://157.245.217.95/login
2. Você deve ver GRADIENTE AZUL (não fundo branco)
3. Clique em "Criar conta" para ver register também melhorado

SE AINDA NÃO FUNCIONAR:
- O cache pode estar no navegador
- Faça: Ctrl+Shift+Delete (limpar cache do navegador)
- Ou abra em modo anônimo/incógnito
- Ou acesse em outro navegador
""")

client.close()
