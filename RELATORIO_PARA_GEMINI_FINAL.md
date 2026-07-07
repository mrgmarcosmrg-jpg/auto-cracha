# 🚀 RELATÓRIO FINAL - ESTADO DO PROJETO PARA GEMINI

**Data:** 2026-06-29  
**Status:** ⚠️ Última milha - Login bloqueado por erro de schema no banco de dados  
**Acesso:** SSH funcionando autonomamente (157.245.217.95, Deploy@123456)

---

## ✅ O QUE JÁ FOI FEITO

1. **Infraestrutura Docker**: ✅ Todos 4 containers rodando (postgres, redis, backend, frontend)
2. **CORS Middleware**: ✅ Configurado corretamente, headers de CORS presentes
3. **Frontend**: ✅ Página de login carregando, redirecionando de `/` para `/login`
4. **API Wrapper**: ✅ Frontend enviando requisições para `http://157.245.217.95:8000`
5. **Auth Schema**: ✅ Alterado para aceitar `password` (não apenas `senha`)
6. **Conexão ao Banco**: ✅ Backend consegue conectar ao PostgreSQL

---

## ❌ PROBLEMA CRÍTICO: Schema de Banco Incompleto

### O Erro

```
POST /auth/login → Error 500
sqlalchemy.exc.ProgrammingError: column usuarios.tenant_id does not exist
```

### Causa Raiz

A tabela `usuarios` foi criada **manualmente com SQL simples** e está **INCOMPLETA**:

**Colunas que existem:**
- id ✅
- email ✅
- nome ✅
- senha_hash ✅
- papel ✅ (mas modelo espera "perfil")
- ativo ✅

**Colunas que FALTAM (modelo espera):**
- tenant_id ❌ → ForeignKey para tenants
- filial_id ❌ → ForeignKey para filiais
- convite_token ❌
- convite_expira_em ❌
- reset_token ❌
- reset_token_expira_em ❌
- atualizado_em ❌
- perfil ❌ (está como "papel", tipo ENUM)

---

## 📊 Evidência Técnica

### Modelo SQLAlchemy (app/models/usuario.py)

```python
class Usuario(Base):
    __tablename__ = "usuarios"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))  # FALTA!
    filial_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("filiais.id"))  # FALTA!
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(Enum(PerfilUsuario))  # Mas tabela tem "papel"
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    convite_token: Mapped[Optional[str]] = mapped_column(String)  # FALTA!
    convite_expira_em: Mapped[Optional[datetime]] = mapped_column(DateTime)  # FALTA!
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())  # FALTA!
```

### Tabela atual no banco (SELECT * FROM usuarios)

```
 id | email | nome | senha_hash | papel | ativo
```

### Migrations disponíveis

- 0001_initial_schema.py ✅ (cria schema completo com todos os campos)
- 0002_reset_token_usuarios.py
- 0003_logo_grupo_tenant.py
- 0004_criado_em_consentimento.py
- 0005_assinatura_pagamento.py

---

## 🔧 SOLUÇÃO NECESSÁRIA

### Opção A: Rodar Migrations do Alembic (PREFERIDO)

O arquivo `0001_initial_schema.py` EXISTE e criaria a tabela corretamente!

Mas Alembic estava falhando com: `ModuleNotFoundError: No module named 'app'`

**Precisa fazer:**
1. Descobrir como rodar Alembic **dentro do container** com o Python path correto
2. Ou usar `docker exec crachapp_backend alembic upgrade head` com PYTHONPATH configurado
3. Ou executar as migrations programaticamente via FastAPI startup

### Opção B: Recrear tabela manualmente com SQL correto

```sql
DROP TABLE usuarios;

CREATE TABLE usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    filial_id UUID REFERENCES filiais(id) ON DELETE SET NULL,
    nome VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    senha_hash VARCHAR NOT NULL,
    perfil ENUM('SUPER_ADMIN', 'ADMIN_TENANT', 'GESTOR_FILIAL', 'VISUALIZADOR') NOT NULL,
    ativo BOOLEAN DEFAULT true,
    convite_token VARCHAR,
    convite_expira_em TIMESTAMP,
    reset_token VARCHAR,
    reset_token_expira_em TIMESTAMP,
    criado_em TIMESTAMP DEFAULT now(),
    atualizado_em TIMESTAMP DEFAULT now()
);

INSERT INTO usuarios (email, nome, senha_hash, perfil, ativo)
VALUES ('admin@crachapp.com.br', 'Administrador', 'HASH_CORRETO', 'SUPER_ADMIN', true);
```

---

## 📋 CHECKLIST PARA GEMINI

- [ ] Verificar se Alembic pode ser executado dentro do container
- [ ] Se sim: rodar `alembic upgrade head` para criar tabelas com schema completo
- [ ] Se não: usar método SQL alternativo para recriar tabela
- [ ] Confirmar tabela tem todos os 14 campos esperados
- [ ] Testar login POST /auth/login com email admin@crachapp.com.br
- [ ] Verificar se retorna `access_token` no JSON

---

## 🌐 Status da Aplicação

| Componente | Status | Notas |
|-----------|--------|-------|
| Docker | ✅ Todos rodando | postgres, redis, backend, frontend |
| Frontend | ✅ Página de login | Renderizando corretamente |
| Backend API | ✅ Respondendo | /health retorna 200 |
| CORS | ✅ Funcionando | Headers presentes |
| Database | ⚠️ Conectando mas schema incompleto | Faltam colunas |
| Login | ❌ Erro 500 | Causa: schema incompleto |

---

## 🔗 Arquivos Relevantes

- Migration principal: `/home/deploy/auto_cracha/backend/alembic/versions/0001_initial_schema.py`
- Modelo: `/home/deploy/auto_cracha/backend/app/models/usuario.py`
- Rota de login: `/home/deploy/auto_cracha/backend/app/routes/auth.py` (linha 74)

---

**Próximo passo:** Gemini analisar e escolher entre Opção A (migrations) ou B (SQL manual) para corrigir o schema do banco de dados.

