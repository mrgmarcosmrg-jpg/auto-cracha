# CONTEXTO DO PROJETO CRACHAPP

## Status Atual
- **Backend:** 100% funcional em produção (port 8000)
- **Frontend:** Estrutura pronta mas CSS/Tailwind não compila corretamente
- **Database:** PostgreSQL 15 - saudável
- **Servidor:** DigitalOcean 157.245.217.95 (Ubuntu 24.04)
- **Docker:** 4 containers (backend, frontend, postgres, redis)

## Problema Principal
CSS/Tailwind não está sendo aplicado ao frontend apesar de múltiplas tentativas:
- Arquivos .tsx foram editados com novo CSS
- Docker rebuild foi feito várias vezes
- Arquivo chega ao servidor MAS não aparece visualmente no navegador
- Tailwind.config.ts está correto
- Dockerfile foi corrigido com RUN rm -rf .next

## O que já foi tentado
1. docker-compose build --no-cache
2. docker-compose rm -f frontend
3. Remover imagem Docker
4. Limpar build cache
5. Copiar arquivos via SCP/SFTP múltiplas vezes
6. Reconstruir Dockerfile

## Próximo Passo Necessário
- Instalar Docker localmente no Windows
- Testar build do Next.js localmente ANTES de enviar pro servidor
- Verificar se Tailwind está compilando corretamente localmente

## Credenciais & Acessos
- IP: 157.245.217.95
- SSH: root@157.245.217.95 (Deploy@123456)
- Email admin: admin@crachapp.com.br (Admin0123456)
- Nginx: porta 443 (HTTPS)

## Arquivos Locais Importantes
- `auto_cracha/frontend-web/tailwind.config.ts` ✓ (correto)
- `auto_cracha/frontend-web/Dockerfile` ✓ (corrigido)
- Páginas melhoradas: dashboard, login, register, colaboradores, lotes
