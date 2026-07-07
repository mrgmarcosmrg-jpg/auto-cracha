import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("=== LOGS DO BACKEND (ultimas 100 linhas) ===")
stdin, stdout, stderr = client.exec_command('docker logs crachapp_backend 2>&1')
logs = stdout.read().decode()
lines = logs.split('\n')
for line in lines[-100:]:
    print(line)

client.close()
