import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.usuario import PerfilUsuario


class ConvidarUsuarioRequest(BaseModel):
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    filial_id: Optional[uuid.UUID] = None


class UsuarioUpdate(BaseModel):
    perfil: Optional[PerfilUsuario] = None
    filial_id: Optional[uuid.UUID] = None


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    filial_id: Optional[uuid.UUID] = None
    ativo: bool
    criado_em: datetime
