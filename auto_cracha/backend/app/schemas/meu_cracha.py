from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

PIN_PATTERN = r"^\d{4}$"


class MeuCrachaOut(BaseModel):
    nome: str
    cargo: str
    foto_url: Optional[str] = None
    exibir_contato_pessoal: bool
    status: str
    tem_dados_medicos: bool
    data_nascimento: Optional[date] = None
    contato_emergencia_nome: Optional[str] = None
    contato_emergencia_tel: Optional[str] = None


class ContatoVisivelRequest(BaseModel):
    exibir_contato_pessoal: bool


class DadosMedicosCampos(BaseModel):
    data_nascimento: Optional[date] = None
    tipo_sanguineo: Optional[str] = None
    comorbidades: Optional[str] = None
    remedios_eventuais: Optional[str] = None
    remedios_continuos: Optional[str] = None
    plano_saude: Optional[str] = None
    alergenicos: Optional[str] = None
    contato_emergencia_nome: Optional[str] = None
    contato_emergencia_tel: Optional[str] = None


class CriarDadosMedicosRequest(DadosMedicosCampos):
    pin: str = Field(min_length=4, max_length=4, pattern=PIN_PATTERN)


class AtualizarDadosMedicosRequest(DadosMedicosCampos):
    pin_atual: str = Field(min_length=4, max_length=4, pattern=PIN_PATTERN)


class AlterarPinRequest(BaseModel):
    pin_atual: str = Field(min_length=4, max_length=4, pattern=PIN_PATTERN)
    pin_novo: str = Field(min_length=4, max_length=4, pattern=PIN_PATTERN)
