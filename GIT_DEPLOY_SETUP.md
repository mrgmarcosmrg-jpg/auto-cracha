# Git Deploy Automático - Setup Completo

## Passo 1: Criar Repositório no GitHub ✅

1. Acesse https://github.com/new
2. **Repository name:** `auto-cracha`
3. **Description:** CrachApp - Badge generation SaaS
4. **Visibility:** Public (recomendado) ou Private
5. ❌ **NÃO** inicialize com README/LICENSE
6. Clique em "Create repository"

## Passo 2: Conectar Repositório Local (Windows)

```powershell
cd "C:\Users\GC-ACERECOM-G-E-F\Desktop\auto cracha"

# Usar o caminho completo do git
$gitPath = "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd\git.exe"

# Adicionar remote
& $gitPath remote add origin https://github.com/mrgmarcosmrg-jpg/auto-cracha.git
& $gitPath branch -M main
& $gitPath push -u origin main
```

**Quando pedir credenciais:**
- Username: `mrgmarcosmrg-jpg`
- Password: **Token de acesso pessoal** (não a senha da conta)

### Gerar Token de Acesso (GitHub):
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token (classic)"
3. Escopos necessários:
   - ✅ `repo` (acesso completo ao repositório)
   - ✅ `admin:repo_hook` (gerenciar webhooks)
4. Generate → Copie o token (⚠️ não será exibido novamente)
5. Use este token como "password" no comando acima

## Passo 3: Configurar Webhook no DigitalOcean

1. GitHub → Seu repositório → Settings → Webhooks → Add webhook
2. **Payload URL:** `http://157.245.217.95:3001/webhook`
3. **Content type:** `application/json`
4. **Which events?** Selecione: `Push events`
5. ✅ Active
6. Clique em "Add webhook"

## Passo 4: Configurar Script de Deploy no Servidor

SSH no servidor e execute:

```bash
# Criar diretório para webhook
mkdir -p /home/deploy/webhook
cd /home/deploy/webhook

# Criar arquivo de script
cat > deploy.sh << 'EOF'
#!/bin/bash
REPO_PATH="/home/deploy/auto_cracha"
cd $REPO_PATH
git fetch origin main
git reset --hard origin/main
cd frontend-web
docker-compose -f ../docker-compose.yml build --no-cache frontend
docker-compose -f ../docker-compose.yml up -d frontend
echo "✅ Deploy concluído em $(date)" >> /var/log/deploy.log
EOF

chmod +x deploy.sh

# Instalar webhook simples (Node.js)
npm install -g github-webhook-handler

# Criar receiver (salvar como webhook-receiver.js)
cat > webhook-receiver.js << 'EOF'
const http = require('http');
const { exec } = require('child_process');

http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/webhook') {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      console.log('Webhook recebido, executando deploy...');
      exec('/home/deploy/webhook/deploy.sh', (err) => {
        if (err) console.error('Deploy falhou:', err);
        else console.log('Deploy bem-sucedido!');
      });
      res.writeHead(200);
      res.end('OK');
    });
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
}).listen(3001);

console.log('Webhook listener rodando na porta 3001');
EOF

# Iniciar receiver em background
nohup node webhook-receiver.js > webhook.log 2>&1 &
echo "✅ Webhook receiver iniciado"
```

## Resumo do Fluxo

```
Você faz push → GitHub
         ↓
GitHub dispara webhook (POST http://157.245.217.95:3001/webhook)
         ↓
Servidor recebe webhook
         ↓
Script deploy.sh executa:
  - git pull origin main
  - docker build frontend
  - docker-compose up -d
         ↓
Página disponível em http://157.245.217.95:3000
```

## Testar Deploy

1. Faça uma mudança no código local
2. `git add .` e `git commit -m "test"`
3. `git push origin main`
4. Verifique em GitHub → Webhooks → Histórico de entrega
5. Acesse http://157.245.217.95:3000 para ver a mudança

## Troubleshooting

**Webhook não dispara?**
- Verifique em GitHub → Repo → Settings → Webhooks → Ver histórico
- Status 200 OK = webhook chegou ao servidor
- Verifique logs do servidor: `tail -f /var/log/deploy.log`

**Deploy falha?**
- SSH ao servidor e verifique: `ps aux | grep webhook`
- Logs: `cat /home/deploy/webhook/webhook.log`
- Certifique-se que docker-compose está no REPO_PATH
