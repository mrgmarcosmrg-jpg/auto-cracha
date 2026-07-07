import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

stdin, stdout, stderr = client.exec_command('cat /home/deploy/auto_cracha/backend/app/schemas/auth.py')
print(stdout.read().decode())

client.close()
