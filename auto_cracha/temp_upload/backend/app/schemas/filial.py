import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FilialCreate(BaseModel):
    nome: str
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    logo_filial_url: Optional[str] = None
    logo_grupo_url: Optional[str] = None


class FilialUpdate(BaseModel):
    nome: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    logo_filial_url: Optional[str] = None
    logo_grupo_url: Optional[str] = None
    ativo: Optional[bool] = None


class FilialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    logo_filial_url: Optional[str] = None
    logo_grupo_url: Optional[str] = None
    ativo: bool
