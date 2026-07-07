import paramiko
import sys

try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

    stdin, stdout, stderr = client.exec_command('cd /home/deploy/auto_cracha && pwd && docker ps -a')

    output = stdout.read().decode()
    print(output)

    error = stderr.read().decode()
    if error:
        print("ERRO:", error)

    client.close()
    print("\nSSH conectado com sucesso!")

except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)
