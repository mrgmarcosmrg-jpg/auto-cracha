# 🎯 PLANO DE AÇÃO GEMINI - CORREÇÃO FRONTEND BLOQUEADO

**Criado por:** Gemini (Consultor Externo)  
**Traduzido por:** Claude Code  
**Data:** 2026-06-25  
**Urgência:** 🔴 CRÍTICA

---

## 📋 RESUMO EXECUTIVO

✅ **Backend, Database e Redis:** Funcionando perfeitamente  
❌ **Frontend:** Bloqueado no placeholder (arquivo não foi copiado via scp)  
🎯 **Solução:** Usar Digital Ocean Console para executar comandos de verificação e rebuild

---

## 🚀 PLANO DE AÇÃO EM 4 PASSOS

### **PASSO 1: VERIFICAR SE ARQUIVO FOI COPIADO** ✅

**Local:** Digital Ocean Console  
**Objetivo:** Confirmar se page.tsx foi realmente atualizado no servidor

**Comando 1:**
```bash
cd /home/deploy/auto_cracha/frontend-web/src/app
```

**Comando 2:**
```bash
cat page.tsx
```

**O que você verá:**

**CENÁRIO A - Arquivo ANTIGO (PROBLEMA):**
```typescript
export default function Home() {
  return (
    <main>
      <h1>CrachApp</h1>
      <p>Infraestrutura base no ar...</p>
    </main>
  );
}
```
→ **Significa:** Arquivo NÃO foi copiado via scp  
→ **Próximo passo:** Editar manualmente com nano/vi

**CENÁRIO B - Arquivo NOVO (CORRETO):**
```typescript
'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.push('/login');
  }, [router]);
  return null;
}
```
→ **Significa:** Arquivo foi copiado corretamente  
→ **Próximo passo:** Ir para PASSO 2

---

### **PASSO 1B: SE ARQUIVO ESTIVER ANTIGO - EDITAR MANUALMENTE**

Se você viu o CENÁRIO A acima, execute:

**Comando:**
```bash
nano /home/deploy/auto_cracha/frontend-web/src/app/page.tsx
```

**Isso abrirá um editor. Substitua TODO o conteúdo por:**
```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.push('/login');
  }, [router]);

  return null;
}
```

**Para salvar:**
1. Pressione `Ctrl + X`
2. Pressione `Y` (Yes)
3. Pressione `Enter`

---

### **PASSO 2: LIMPEZA FORÇADA E REBUILD**

**Local:** Digital Ocean Console  
**Objetivo:** Remover container antigo e reconstruir do zero

**Comando 1 - Ir para diretório:**
```bash
cd /home/deploy/auto_cracha
```

**Comando 2 - Parar container:**
```bash
docker-compose stop frontend
```

**Comando 3 - Remover container:**
```bash
docker-compose rm -f frontend
```

**Comando 4 - Limpar cache do Next.js:**
```bash
rm -rf frontend-web/.next
```

**Comando 5 - Rebuild SEM CACHE:**
```bash
docker-compose build --no-cache frontend
```

⏳ **AGUARDE 3-5 MINUTOS** - O build pode demorar!  
Você verá: `npm install`, `npm run build`, etc.

**Comando 6 - Iniciar novo container:**
```bash
docker-compose up -d frontend
```

**Comando 7 - Aguardar estabilização:**
```bash
sleep 5
```

---

### **PASSO 3: VERIFICAR LOGS DO BUILD**

**Local:** Digital Ocean Console  
**Objetivo:** Confirmar se o build foi bem-sucedido

**Comando 1 - Ver status dos containers:**
```bash
docker ps | grep frontend
```

Você deve ver algo como:
```
crachapp_frontend   "node /app/server.js"   Up X seconds   0.0.0.0:3000->3000/tcp
```

**Comando 2 - Ver logs completos:**
```bash
docker logs crachapp_frontend
```

**Procure por:**
- ✅ `Ready in XXXms` = Sucesso!
- ❌ `Error:` ou `Failed to compile` = Problema!

**Se houver erro, cole o erro aqui:**
```
[Cole os logs do erro aqui]
```

---

### **PASSO 4: TESTE FINAL**

**Local:** Seu navegador  
**Objetivo:** Verificar se tela de login aparece

**Teste 1 - Modo Normal:**
1. Abra: http://157.245.217.95:3000
2. Pressione: `Ctrl + Shift + R` (hard refresh)
3. **Esperado:** Tela de LOGIN (não placeholder)

**Teste 2 - Modo Anônimo (sem cache):**
1. Abra uma janela anônima/privada
2. Acesse: http://157.245.217.95:3000
3. **Esperado:** Tela de LOGIN (não placeholder)

**Se vir a tela de login, faça o teste final:**
```
Email: admin@crachapp.com.br
Senha: Admin0123456
```

✅ Se conseguir logar = **PROBLEMA RESOLVIDO!** 🎉

---

## ⚠️ SE O PROBLEMA PERSISTIR

Se após o PASSO 4 o placeholder ainda aparecer, execute:

### **SOLUÇÃO ALTERNATIVA 1: Usar redirect() em Server Component**

**Edite manualmente page.tsx no console:**
```bash
nano /home/deploy/auto_cracha/frontend-web/src/app/page.tsx
```

**Substitua por:**
```typescript
import { redirect } from 'next/navigation';

export default function Home() {
  redirect('/login');
}
```

Depois repita PASSO 2 (rebuild).

---

### **SOLUÇÃO ALTERNATIVA 2: Configurar Redirect em next.config.js**

**Edite next.config.js:**
```bash
nano /home/deploy/auto_cracha/frontend-web/next.config.js
```

**Adicione isso dentro de `const nextConfig = {`:**
```javascript
async redirects() {
  return [
    {
      source: '/',
      destination: '/login',
      permanent: true,
    },
  ]
},
```

**Exemplo completo:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  async redirects() {
    return [
      {
        source: '/',
        destination: '/login',
        permanent: true,
      },
    ]
  },
};

module.exports = nextConfig;
```

Depois repita PASSO 2 (rebuild).

---

## ✅ CHECKLIST DE EXECUÇÃO

Use este checklist enquanto executa os passos:

```
PASSO 1 - VERIFICAÇÃO DE ARQUIVO
☐ Navegou até /home/deploy/auto_cracha/frontend-web/src/app
☐ Executou: cat page.tsx
☐ Verificou conteúdo (antigo ou novo?)
☐ Se antigo: Editou com nano

PASSO 2 - LIMPEZA E REBUILD
☐ Parou container: docker-compose stop frontend
☐ Removeu container: docker-compose rm -f frontend
☐ Limpou cache: rm -rf frontend-web/.next
☐ Rebuild sem cache: docker-compose build --no-cache frontend
☐ Iniciou novo container: docker-compose up -d frontend
☐ Aguardou 5 minutos

PASSO 3 - VERIFICAÇÃO DOS LOGS
☐ Verificou status: docker ps | grep frontend
☐ Viu container "Up" (rodando)
☐ Verificou logs: docker logs crachapp_frontend
☐ Procurou por "Ready in XXXms" (sucesso)
☐ Não há mensagens de erro

PASSO 4 - TESTE FINAL
☐ Abriu http://157.245.217.95:3000
☐ Pressinou Ctrl+Shift+R
☐ Viu TELA DE LOGIN (não placeholder)
☐ Testou login: admin@crachapp.com.br / Admin0123456
☐ ✅ LOGIN FUNCIONOU!
```

---

## 🆘 SUPORTE

Se algo der errado:

1. **Qual foi o erro?** Cole aqui o resultado do `docker logs crachapp_frontend`
2. **O arquivo mudou?** Cole o resultado de `cat page.tsx`
3. **O container iniciou?** Cole o resultado de `docker ps | grep frontend`

---

## 📊 MÉTRICAS DE SUCESSO

| Item | Status | Confirmado |
|------|--------|-----------|
| Arquivo page.tsx atualizado | ✅ | Passo 1 |
| Container rebuilt | ✅ | Passo 2 |
| Logs sem erro | ✅ | Passo 3 |
| Tela de login aparece | ✅ | Passo 4 |
| Login funciona | ✅ | Passo 4 |

---

**Se todos os itens forem ✅, a Etapa 9 está CONCLUÍDA!** 🎉

---

**Próximos passos após sucesso:**
- Testar fluxos de pagamento
- Verificar UX mobile
- Configurar SSL/HTTPS (v2.0)
- Deploy em produção final
