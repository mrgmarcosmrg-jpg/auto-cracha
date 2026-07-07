import uuid
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.dependencies import require_admin_tenant
from app.models.usuario import Usuario
from app.schemas.usuario import ConvidarUsuarioRequest, UsuarioOut, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _obter_usuario_do_tenant(db: Session, usuario_id: uuid.UUID, tenant_id) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.tenant_id == tenant_id).first()
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuário não encontrado")
    return usuario


@router.get("", response_model=List[UsuarioOut])
def listar_usuarios(
    usuario_logado: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    return (
        db.query(Usuario)
        .filter(Usuario.tenant_id == usuario_logado.tenant_id)
        .order_by(Usuario.criado_em)
        .all()
    )


@router.post("/convidar", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def convidar_usuario(
    payload: ConvidarUsuarioRequest,
    usuario_logado: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    if db.query(Usuario).filter(Usuario.email == payload.email).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "E-mail já cadastrado")

    convite_token = uuid.uuid4().hex
    novo_usuario = Usuario(
        tenant_id=usuario_logado.tenant_id,
        filial_id=payload.filial_id,
        nome=payload.nome,
        email=payload.email,
        senha_hash="",
        perfil=payload.perfil,
        ativo=False,
        convite_token=convite_token,
        convite_expira_em=datetime.utcnow() + timedelta(hours=48),
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)

    link = f"{settings.APP_URL}/convite/{convite_token}"
    print(f"[DEV] Link de convite para {novo_usuario.email}: {link}")

    return novo_usuario


@router.put("/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(
    usuario_id: uuid.UUID,
    payload: UsuarioUpdate,
    usuario_logado: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_do_tenant(db, usuario_id, usuario_logado.tenant_id)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(usuario, campo, valor)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/{usuario_id}/revogar", status_code=status.HTTP_204_NO_CONTENT)
def revogar_usuario_acesso(
    usuario_id: uuid.UUID,
    usuario_logado: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_do_tenant(db, usuario_id, usuario_logado.tenant_id)
    usuario.ativo = False
    db.commit()


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def revogar_usuario(
    usuario_id: uuid.UUID,
    usuario_logado: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    usuario = _obter_usuario_do_tenant(db, usuario_id, usuario_logado.tenant_id)
    usuario.ativo = False
    db.commit()
