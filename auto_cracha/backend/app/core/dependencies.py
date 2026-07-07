import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_access_token
from app.models.usuario import PerfilUsuario, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        if user_id is None or tenant_id is None:
            raise CREDENCIAIS_INVALIDAS
    except JWTError:
        raise CREDENCIAIS_INVALIDAS

    usuario = db.query(Usuario).filter(Usuario.id == uuid.UUID(user_id)).first()
    if usuario is None or not usuario.ativo:
        raise CREDENCIAIS_INVALIDAS

    # Usa tenant_id do JWT e salva no banco se diferente
    tenant_uuid = uuid.UUID(tenant_id)
    if usuario.tenant_id != tenant_uuid:
        usuario.tenant_id = tenant_uuid
        db.commit()

    return usuario


def require_admin_tenant(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil not in (PerfilUsuario.ADMIN_TENANT, PerfilUsuario.SUPER_ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a administradores da empresa")
    return usuario


def require_gestor_or_above(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil not in (
        PerfilUsuario.GESTOR_FILIAL,
        PerfilUsuario.ADMIN_TENANT,
        PerfilUsuario.SUPER_ADMIN,
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito a gestores de filial ou superior")
    return usuario


def require_super_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if usuario.perfil != PerfilUsuario.SUPER_ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Acesso restrito ao super admin")
    return usuario


def montar_filtro_tenant(usuario: Usuario) -> dict:
    """Filtro de isolamento multitenant a aplicar nas queries do endpoint atual.

    SUPER_ADMIN não tem filtro (acessa tudo). ADMIN_TENANT e VISUALIZADOR filtram só
    por tenant_id. GESTOR_FILIAL filtra por tenant_id + filial_id (só sua filial).
    """
    if usuario.perfil == PerfilUsuario.SUPER_ADMIN:
        return {}

    filtro = {"tenant_id": usuario.tenant_id}
    if usuario.perfil == PerfilUsuario.GESTOR_FILIAL:
        filtro["filial_id"] = usuario.filial_id
    return filtro


def get_tenant_filter(usuario: Usuario = Depends(get_current_user)) -> dict:
    return montar_filtro_tenant(usuario)
