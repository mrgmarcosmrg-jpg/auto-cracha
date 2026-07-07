import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models.assinatura import Assinatura, StatusAssinatura
from app.models.config_empresa import ConfigEmpresa
from app.models.tenant import StatusTenant, Tenant
from app.models.usuario import PerfilUsuario, Usuario
from app.schemas.auth import (
    AceitarConviteRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _gerar_token(usuario: Usuario) -> TokenResponse:
    access_token = create_access_token(
        {
            "user_id": str(usuario.id),
            "tenant_id": str(usuario.tenant_id) if usuario.tenant_id else None,
            "filial_id": str(usuario.filial_id) if usuario.filial_id else None,
            "perfil": usuario.perfil.value,
        }
    )
    return TokenResponse(access_token=access_token)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(Tenant).filter(Tenant.cnpj == payload.cnpj).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "CNPJ já cadastrado")
    if db.query(Usuario).filter(Usuario.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "E-mail já cadastrado")

    tenant = Tenant(
        nome_empresa=payload.nome_empresa,
        cnpj=payload.cnpj,
        email_admin=payload.email,
        status=StatusTenant.TRIAL,
        trial_expira_em=datetime.utcnow() + timedelta(days=7),
    )
    db.add(tenant)
    db.flush()

    usuario = Usuario(
        tenant_id=tenant.id,
        nome=payload.nome_responsavel,
        email=payload.email,
        senha_hash=hash_password(payload.senha),
        perfil=PerfilUsuario.ADMIN_TENANT,
        ativo=True,
    )
    db.add(usuario)
    db.add(Assinatura(tenant_id=tenant.id, status=StatusAssinatura.TRIAL, max_colaboradores=5))
    db.add(ConfigEmpresa(tenant_id=tenant.id))

    db.commit()
    db.refresh(usuario)
    return _gerar_token(usuario)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if not usuario or not usuario.ativo or not verify_password(payload.senha, usuario.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
    return _gerar_token(usuario)


@router.post("/refresh", response_model=TokenResponse)
def refresh(usuario: Usuario = Depends(get_current_user)):
    return _gerar_token(usuario)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == payload.email).first()
    if usuario:
        usuario.reset_token = uuid.uuid4().hex
        usuario.reset_token_expira_em = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        link = f"{settings.APP_URL}/reset-password/{usuario.reset_token}"
        print(f"[DEV] Link de redefinição de senha para {usuario.email}: {link}")

    # Resposta genérica: não revela se o e-mail está cadastrado.
    return {"detail": "Se o e-mail existir, um link de redefinição foi enviado."}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.reset_token == payload.token).first()
    if not usuario or not usuario.reset_token_expira_em or usuario.reset_token_expira_em < datetime.utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido ou expirado")

    usuario.senha_hash = hash_password(payload.nova_senha)
    usuario.reset_token = None
    usuario.reset_token_expira_em = None
    db.commit()
    return {"detail": "Senha redefinida com sucesso."}


@router.post("/aceitar-convite/{token}", response_model=TokenResponse)
def aceitar_convite(token: str, payload: AceitarConviteRequest, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.convite_token == token).first()
    if not usuario or not usuario.convite_expira_em or usuario.convite_expira_em < datetime.utcnow():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Convite inválido ou expirado")

    usuario.senha_hash = hash_password(payload.senha)
    usuario.ativo = True
    usuario.convite_token = None
    usuario.convite_expira_em = None
    db.commit()
    db.refresh(usuario)
    return _gerar_token(usuario)
