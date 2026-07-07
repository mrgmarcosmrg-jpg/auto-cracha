import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.colaborador import StatusColaborador


class ColaboradorCreate(BaseModel):
    nome: str
    cargo: str
    celular: str
    email_colaborador: Optional[EmailStr] = None
    filial_id: Optional[uuid.UUID] = None
    cpf: Optional[str] = None
    em_treinamento: bool = False
    pcd: bool = False
    pcd_descricao: Optional[str] = None
    campos_adicionais: Optional[dict] = None


class ColaboradorUpdate(BaseModel):
    nome: Optional[str] = None
    cargo: Optional[str] = None
    celular: Optional[str] = None
    email_colaborador: Optional[EmailStr] = None
    filial_id: Optional[uuid.UUID] = None
    cpf: Optional[str] = None
    em_treinamento: Optional[bool] = None
    pcd: Optional[bool] = None
    pcd_descricao: Optional[str] = None
    campos_adicionais: Optional[dict] = None


class ColaboradorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filial_id: uuid.UUID
    status: StatusColaborador
    qr_token: uuid.UUID
    nome: str
    cargo: str
    celular: Optional[str] = None
    email_colaborador: Optional[str] = None
    em_treinamento: bool
    pcd: bool
    pcd_descricao: Optional[str] = None
    campos_adicionais: Optional[dict] = None
    foto_url: Optional[str] = None
    data_desligamento: Optional[datetime] = None
    criado_em: datetime


class LinkLgpdOut(BaseModel):
    link: str
    whatsapp_url: str


class ColaboradorCriadoOut(ColaboradorOut):
    link_lgpd: LinkLgpdOut


class ErroImportacao(BaseModel):
    linha: int
    motivo: str


class ImportarResultado(BaseModel):
    importados: int
    erros: list[ErroImportacao]
