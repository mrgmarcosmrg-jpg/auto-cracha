# 🚨 INSTRUÇÕES DE DEPLOY MANUAL - CRACHAPP

**Situação:** SSH está com problemas. Você precisa executar manualmente no console da DigitalOcean.

---

## ✅ PASSO 1: Copiar os Arquivos Novos

Abra o painel da DigitalOcean e clique em "Console" para acessar o terminal do servidor.

Depois execute **um por um** os comandos abaixo:

### 1a. Criar arquivo login_html.py

```bash
cat > /home/deploy/auto_cracha/backend/app/routes/login_html.py << 'ENDOFFILE'
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CrachApp - Login</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 100%;
            padding: 40px;
        }

        .logo {
            text-align: center;
            margin-bottom: 30px;
        }

        .logo-icon {
            font-size: 48px;
            margin-bottom: 10px;
        }

        .logo h1 {
            font-size: 28px;
            color: #1a202c;
            margin-bottom: 5px;
        }

        .logo p {
            color: #718096;
            font-size: 14px;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #2d3748;
            font-weight: 500;
            font-size: 14px;
        }

        input[type="email"],
        input[type="password"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
        }

        input[type="email"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .error-message {
            background-color: #fed7d7;
            color: #c53030;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
            font-size: 14px;
            border: 1px solid #fc8181;
        }

        .error-message.show {
            display: block;
        }

        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .links {
            margin-top: 20px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            text-align: center;
            font-size: 14px;
        }

        .links a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s;
        }

        .links a:hover {
            color: #764ba2;
        }

        .divider {
            color: #cbd5e0;
            margin: 0 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <div class="logo-icon">🆔</div>
            <h1>CrachApp</h1>
            <p>Geração de crachás inteligentes</p>
        </div>

        <div class="error-message" id="errorMsg"></div>

        <form id="loginForm">
            <div class="form-group">
                <label for="email">E-mail</label>
                <input
                    type="email"
                    id="email"
                    name="email"
                    placeholder="seu@email.com"
                    value="admin@crachapp.com.br"
                    required
                >
            </div>

            <div class="form-group">
                <label for="senha">Senha</label>
                <input
                    type="password"
                    id="senha"
                    name="senha"
                    placeholder="••••••••"
                    value="Admin0123456"
                    required
                >
            </div>

            <button type="submit" id="submitBtn">Entrar</button>
        </form>

        <div class="links">
            <a href="/forgot-password">Esqueci minha senha</a>
            <span class="divider">•</span>
            <a href="/register">Criar conta</a>
        </div>
    </div>

    <script>
        const form = document.getElementById('loginForm');
        const emailInput = document.getElementById('email');
        const senhaInput = document.getElementById('senha');
        const submitBtn = document.getElementById('submitBtn');
        const errorMsg = document.getElementById('errorMsg');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            submitBtn.disabled = true;
            submitBtn.textContent = 'Entrando...';
            errorMsg.classList.remove('show');

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        email: emailInput.value,
                        senha: senhaInput.value
                    })
                });

                if (!response.ok) {
                    const error = await response.json().catch(() => ({ detail: 'Erro ao conectar' }));
                    throw new Error(error.detail || 'Erro ao fazer login');
                }

                const data = await response.json();

                // Salvar token no localStorage
                localStorage.setItem('access_token', data.access_token);

                // Redirecionar para dashboard
                window.location.href = '/dashboard.html';

            } catch (error) {
                errorMsg.textContent = error.message;
                errorMsg.classList.add('show');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Entrar';
            }
        });
    </script>
</body>
</html>
"""

@router.get("/login-html", response_class=HTMLResponse)
async def login_html():
    """Página de login em HTML puro (sem Next.js)"""
    return LOGIN_HTML
ENDOFFILE
```

---

### 1b. Atualizar main.py com CORS corrigido

```bash
cat > /home/deploy/auto_cracha/backend/main.py << 'ENDOFFILE'
from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.routes import auth, colaboradores, config, cracha, filiais, lotes, meu_cracha, pagamento, publico, usuarios, login_html

app = FastAPI(title="CrachApp API")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app.add_middleware(SecurityHeadersMiddleware)

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://157.245.217.95:3000",
    "http://157.245.217.95:8000",
    os.environ.get("APP_URL", "https://crachapp.com.br"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(config.router)
app.include_router(filiais.router)
app.include_router(colaboradores.router)
app.include_router(cracha.router)
app.include_router(lotes.router)
app.include_router(publico.router)
app.include_router(meu_cracha.router)
app.include_router(pagamento.router)
app.include_router(login_html.router)


@app.get("/health")
def health():
    """Verificação de saúde da aplicação com status de dependências."""
    from app.core.db import get_db

    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "dependencies": {
            "database": "checking",
            "mercado_pago": "checking",
            "cloudinary": "checking",
        }
    }

    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        status["dependencies"]["database"] = "ok"
    except Exception as e:
        status["dependencies"]["database"] = f"error: {str(e)}"
        status["status"] = "degraded"

    mp_token = os.environ.get("MERCADOPAGO_ACCESS_TOKEN", "").strip()
    status["dependencies"]["mercado_pago"] = "ok" if mp_token and mp_token != "TEST_TOKEN" else "not_configured"

    cloudinary_url = os.environ.get("CLOUDINARY_URL", "").strip()
    status["dependencies"]["cloudinary"] = "ok" if cloudinary_url else "not_configured"

    return status
ENDOFFILE
```

---

## ✅ PASSO 2: Rebuild do Backend

Ainda no console da DigitalOcean, execute:

```bash
cd /home/deploy/auto_cracha

# Parar tudo
docker-compose down

# Limpar sistema
docker system prune -af --volumes

# Rebuild
docker-compose build --no-cache backend

# Subir tudo
docker-compose up -d

# Aguardar 30 segundos
sleep 30

# Verificar status
docker-compose ps
```

---

## ✅ PASSO 3: Testar

Abra no navegador: **http://157.245.217.95:8000/login-html**

Você deve ver uma página **COLORIDA** com um formulário de login azul/roxo.

---

## ✅ PASSO 4: Tentar Login

1. E-mail: `admin@crachapp.com.br`
2. Senha: `Admin0123456`
3. Clique em "Entrar"

---

## 🆘 Se Ainda Não Funcionar

1. Verifique os logs: `docker logs crachapp_backend | tail -30`
2. Verifique status: `docker-compose ps`
3. Se backend não estiver UP: `docker restart crachapp_backend`

---

**Tempo estimado:** 15-20 minutos

Avise quando terminar! 👍
