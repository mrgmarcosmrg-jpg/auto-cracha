import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import require_admin_tenant
from app.models.filial import Filial
from app.models.usuario import Usuario
from app.schemas.filial import FilialCreate, FilialOut, FilialUpdate
from app.services.cloudinary_service import upload_imagem

router = APIRouter(prefix="/filiais", tags=["filiais"])


def _obter_filial(db: Session, filial_id: uuid.UUID, tenant_id) -> Filial:
    filial = db.query(Filial).filter(Filial.id == filial_id, Filial.tenant_id == tenant_id).first()
    if not filial:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Filial não encontrada")
    return filial


@router.get("", response_model=List[FilialOut])
def listar_filiais(usuario: Usuario = Depends(require_admin_tenant), db: Session = Depends(get_db)):
    return db.query(Filial).filter(Filial.tenant_id == usuario.tenant_id).order_by(Filial.nome).all()


@router.post("", response_model=FilialOut, status_code=status.HTTP_201_CREATED)
def criar_filial(
    payload: FilialCreate,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    filial = Filial(tenant_id=usuario.tenant_id, **payload.model_dump())
    db.add(filial)
    db.commit()
    db.refresh(filial)
    return filial


@router.put("/{filial_id}", response_model=FilialOut)
def atualizar_filial(
    filial_id: uuid.UUID,
    payload: FilialUpdate,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    filial = _obter_filial(db, filial_id, usuario.tenant_id)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(filial, campo, valor)
    db.commit()
    db.refresh(filial)
    return filial


@router.delete("/{filial_id}", status_code=status.HTTP_204_NO_CONTENT)
def desativar_filial(
    filial_id: uuid.UUID,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    filial = _obter_filial(db, filial_id, usuario.tenant_id)
    filial.ativo = False
    db.commit()


@router.post("/{filial_id}/logo", response_model=FilialOut)
def upload_logo_filial(
    filial_id: uuid.UUID,
    arquivo: UploadFile = File(...),
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    filial = _obter_filial(db, filial_id, usuario.tenant_id)
    filial.logo_filial_url = upload_imagem(arquivo.file.read(), folder=f"filiais/{filial.id}/logo")
    db.commit()
    db.refresh(filial)
    return filial
