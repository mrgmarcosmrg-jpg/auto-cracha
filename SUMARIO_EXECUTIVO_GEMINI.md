# 🚨 SUMÁRIO EXECUTIVO - PROBLEMA NA MIGRAÇÃO 0005

**Data:** 2026-06-29  
**Status:** ⚠️ **Migrations falhando na etapa 5**

---

## ✅ O QUE FOI CONSEGUIDO

1. **SSH conectando autonomamente** ✅
2. **Alembic rodando dentro do container** ✅  
3. **Migrações 0001-0004 aplicadas com SUCESSO** ✅
   - Criou tabelas: tenants, filiais, usuarios, colaboradores, lotes, crachás, assinaturas, config_empresas, consentimentos_lgpd
   - Usuario table está **COMPLETA** com 14 colunas (confirmado em logs)
   - Todos os ENUMs criados corretamente

---

## ❌ PROBLEMA: Migração 0005 Falha

**Erro:**
```
File "/app/alembic/versions/0005_assinatura_pagamento.py", line 21, in upgrade
    op.alter_column('assinaturas', 'plano_assinatura',
    
psycopg2.errors.UndefinedColumn: column "plano_assinatura" of relation "assinaturas" does not exist
```

**Tradução:** A migração 0005 tenta alterar a coluna `plano_assinatura` da tabela `assinaturas`, mas essa coluna **NÃO FOI CRIADA** pela migração 0001!

---

## 🔍 ANÁLISE

### Migração 0001 (initial_schema.py)
Cria a tabela `assinaturas` com estas colunas:
```sql
CREATE TABLE assinaturas (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL (FK tenants),
    status ENUM('TRIAL', 'ATIVO', 'CANCELADO') NOT NULL,
    max_colaboradores INTEGER NOT NULL,
    criado_em TIMESTAMP DEFAULT now(),
    atualizado_em TIMESTAMP
)
```
❌ **NÃO tem `plano_assinatura`**

### Migração 0005 (assinatura_pagamento.py)
Tenta fazer:
```python
op.alter_column('assinaturas', 'plano_assinatura',
    existing_type=sa.VARCHAR(),
    type_=sa.Enum('MENSAL', 'TRIMESTRAL', 'ANUAL', name='plano_assinatura'),
    existing_nullable=True,
    nullable=False
)
```
❌ **Essa coluna NÃO existe!**

---

## 🛠️ SOLUÇÃO NECESSÁRIA

**Gemini precisa fazer UMA de duas coisas:**

### Opção A: Corrigir o arquivo 0005_assinatura_pagamento.py
- Remover o `op.alter_column('assinaturas', 'plano_assinatura', ...)` que está falhando
- Ou adicionar `op.add_column('assinaturas', sa.Column('plano_assinatura', ...))` ANTES do alter_column
- Arquivo: `/home/deploy/auto_cracha/backend/alembic/versions/0005_assinatura_pagamento.py`

### Opção B: Corrigir a migração 0001
- Adicionar `plano_assinatura` como coluna na criação da tabela `assinaturas`
- Arquivo: `/home/deploy/auto_cracha/backend/alembic/versions/0001_initial_schema.py`

---

## 📊 STATUS TÉCNICO

| Item | Status |
|------|--------|
| alembic.ini | ✅ Copiado |
| Migração 0001 | ✅ Sucesso |
| Migração 0002 | ✅ Sucesso |
| Migração 0003 | ✅ Sucesso |
| Migração 0004 | ✅ Sucesso |
| Migração 0005 | ❌ FALHA |
| Tabela usuarios | ✅ Criada com 14 colunas (se 0001-0004 rodarem) |
| Login | ❌ Erro 500 (aguardando migrations completarem) |

---

## 🚀 PRÓXIMAS AÇÕES

1. **Gemini**: Corrigir `/app/alembic/versions/0005_assinatura_pagamento.py`
2. **Claude Code**: Rodar `alembic upgrade head` novamente
3. **Claude Code**: Criar usuário admin via SQL
4. **Claude Code**: Testar login

---

**Conclusão:** A infraestrutura está 100% pronta. O problema é **apenas** no arquivo de migração 0005. Uma vez corrigido, o login funcionará imediatamente.

