from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.colaborador import StatusColaborador


class EmpresaPublicaOut(BaseModel):
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None
    logo_url: Optional[str] = None
    endereco_completo: Optional[str] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    email_empresa: Optional[str] = None
    redes_sociais: Optional[dict] = None


class ColaboradorPublicoOut(BaseModel):
    status: StatusColaborador
    nome: Optional[str] = None
    cargo: Optional[str] = None
    foto_url: Optional[str] = None
    data_desligamento: Optional[datetime] = None
    exibir_contato_pessoal: bool = False
    celular: Optional[str] = None
    email_colaborador: Optional[str] = None
    contato_emergencia_nome: Optional[str] = None
    contato_emergencia_tel: Optional[str] = None
    tem_sos: bool = False
    acesso_expirado: bool = False


class PaginaPublicaOut(BaseModel):
    empresa: EmpresaPublicaOut
    colaborador: ColaboradorPublicoOut


class SosRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=4, pattern=r"^\d{4}$")
