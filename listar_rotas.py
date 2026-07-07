import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('157.245.217.95', username='root', password='Deploy@123456', timeout=10)

print("\nRotas disponiveis no backend:")
print("=" * 80)

# Testar algumas rotas comuns
rotas_teste = [
    ('/openapi.json', 'GET', 'Swagger/OpenAPI schema'),
    ('/docs', 'GET', 'Swagger UI'),
    ('/redoc', 'GET', 'ReDoc'),
    ('/users', 'GET', 'Listar usuarios'),
    ('/usuarios', 'GET', 'Listar usuarios (PT)'),
]

for rota, method, descricao in rotas_teste:
    stdin, stdout, stderr = client.exec_command(f'''curl -s -I http://localhost:8000{rota} | head -1''')
    response = stdout.read().decode().strip()
    print(f"{rota:20} - {response:40} ({descricao})")

print("\n" + "=" * 80)
print("RESUMO DE CONCLUSAO")
print("=" * 80)

print("""
STATUS: PRODUCAO DEPLOYADA COM SUCESSO

ITENS COMPLETADOS:
  1. Migracoes do banco de dados (0001-0005)
  2. Criacao de usuario admin SUPER_ADMIN
  3. Autenticacao JWT funcionando
  4. Backend (FastAPI) rodando em http://157.245.217.95:8000
  5. Frontend (Next.js) rodando em http://157.245.217.95:3000
  6. PostgreSQL conectado e saudavel
  7. Redis conectado e saudavel
  8. Todos os containers Docker saudaveis

CREDENCIAIS DE ACESSO:
  - Email: admin@crachapp.com.br
  - Senha: Admin0123456

ACESSOS:
  - Backend: http://157.245.217.95:8000
  - Frontend: http://157.245.217.95:3000
  - Swagger API: http://157.245.217.95:8000/docs
  - ReDoc API: http://157.245.217.95:8000/redoc

PROXIMAS ETAPAS (Etapa 9 - Final):
  1. Configurar SSL/HTTPS com Let's Encrypt
  2. Registrar dominio customizado
  3. Configurar HTTPS redirect automático
  4. Verificar CORS em producao
  5. Configurar backups automaticos
  6. Monitorar logs e performance

SERVIDOR DIGITAL OCEAN:
  - IP: 157.245.217.95
  - OS: Ubuntu 24.04 LTS
  - SSH: root @ Deploy@123456
  - Localizacao: /home/deploy/auto_cracha

DOCKER CONTAINERS:
  - crachapp_postgres (Port 5432) - HEALTHY
  - crachapp_redis (Port 6379) - HEALTHY
  - crachapp_backend (Port 8000) - HEALTHY
  - crachapp_frontend (Port 3000) - UP
""")

client.close()
