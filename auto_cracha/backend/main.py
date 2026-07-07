from datetime import datetime
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import text

from app.routes import auth, colaboradores, config, cracha, filiais, lotes, meu_cracha, pagamento, publico, usuarios

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
