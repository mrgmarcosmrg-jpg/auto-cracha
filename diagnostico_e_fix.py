import paramiko
import sys

def executar_cmd(client, cmd):
    stdin, stdout, stderr = client.exec_command(cmd)
    return stdout.read().decode(), stderr.read().decode()

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

    print("=" * 60)
    print("1. VERIFICANDO ARQUIVO main.py")
    print("=" * 60)
    out, err = executar_cmd(client, 'cat /home/deploy/auto_cracha/backend/main.py | head -30')
    print(out)

    print("\n" + "=" * 60)
    print("2. VERIFICANDO LOGS DO BACKEND")
    print("=" * 60)
    out, err = executar_cmd(client, 'docker logs crachapp_backend --tail=20')
    print(out)

    print("\n" + "=" * 60)
    print("3. TESTANDO /health NO BACKEND")
    print("=" * 60)
    out, err = executar_cmd(client, 'curl -s http://localhost:8000/health | python -m json.tool')
    print(out)

    print("\n" + "=" * 60)
    print("4. TESTANDO CORS COM Origin header")
    print("=" * 60)
    out, err = executar_cmd(client, 'curl -i -H "Origin: http://157.245.217.95:3000" http://localhost:8000/health 2>&1 | head -15')
    print(out)

    client.close()
    print("\nDiagnostico concluido!")

except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
