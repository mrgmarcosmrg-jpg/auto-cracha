import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("Testando acesso ao login page...")
stdin, stdout, stderr = client.exec_command('curl -k -s https://localhost/login 2>/dev/null')
html = stdout.read().decode()

print("\nTamanho do HTML:", len(html))
print("Tem 'CrachApp'?", 'CrachApp' in html)
print("Tem 'gradient'?", 'gradient' in html)
print("Tem 'from-blue'?", 'from-blue' in html)
print("Tem 'Tailwind'?", 'Tailwind' in html)

if len(html) > 1000:
    print("\n[OK] HTML recebido com sucesso!")
    print("Primeiras 500 caracteres:")
    print(html[:500])

if 'gradient' in html or 'from-blue' in html:
    print("\n✅ CSS GRADIENTE ESTA SENDO RENDERIZADO NO HTML!")
else:
    print("\n⚠️ CSS pode nao estar no HTML")

client.close()
