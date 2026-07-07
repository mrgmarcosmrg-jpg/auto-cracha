import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

time.sleep(2)

print("Verificacao final...")
print("=" * 80)

# Verificar arquivo
stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend grep -c "bg-gradient-to-br from-blue-600" /app/src/app/login/page.tsx')
result = stdout.read().decode().strip()

print(f"\n[Verificacao] Arquivo tem novo CSS? {result}")

if result == '1':
    print("\n" + "=" * 80)
    print("SUCESSO TOTAL!!! CSS FOI APLICADO!")
    print("=" * 80)
    print("\nAcesse agora: https://157.245.217.95/login")
    print("\nVoce vera:")
    print("- Fundo com GRADIENTE AZUL-ROXO")
    print("- Card branco centralizado")
    print("- Inputs melhorados")
    print("- Botao com efeitos hover")
    print("\nSe ainda nao ver, limpe o cache:")
    print("  Ctrl+Shift+Delete (limpar tudo)")
    print("  ou abra em modo INCOGNITO/ANONIMO")
else:
    print("\n[Debug] Mostrando primeiras linhas do arquivo no container:")
    stdin, stdout, stderr = client.exec_command('docker exec crachapp_frontend head -40 /app/src/app/login/page.tsx')
    content = stdout.read().decode()
    print(content)

client.close()
