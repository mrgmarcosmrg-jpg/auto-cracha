from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class ConfigOut(BaseModel):
    # tenant
    nome_empresa: str
    cnpj: str
    logo_url: Optional[str] = None
    logo_grupo_url: Optional[str] = None
    cor_primaria: str
    cor_secundaria: str
    usar_faixa_treinamento: bool
    usar_faixa_pcd: bool
    faixas_customizadas: Optional[list] = None
    status: str
    trial_expira_em: datetime

    # config_empresa
    template_id: str
    setor_sugerido: Optional[str] = None
    campos_adicionais_config: Optional[list] = None
    redes_sociais: Optional[dict] = None
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    email_empresa: Optional[str] = None
    endereco_completo: Optional[str] = None
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None


class IdentidadeUpdate(BaseModel):
    logo_url: Optional[str] = None
    logo_grupo_url: Optional[str] = None
    cor_primaria: Optional[str] = None
    cor_secundaria: Optional[str] = None
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None


class ContatoUpdate(BaseModel):
    telefone: Optional[str] = None
    whatsapp: Optional[str] = None
    email_empresa: Optional[EmailStr] = None
    endereco_completo: Optional[str] = None
    redes_sociais: Optional[dict] = None


class TemplateUpdate(BaseModel):
    template_id: str


class SetorUpdate(BaseModel):
    setor_sugerido: Optional[str] = None
    campos_adicionais_config: Optional[list] = None
    faixas_customizadas: Optional[list] = None
    usar_faixa_treinamento: Optional[bool] = None
    usar_faixa_pcd: Optional[bool] = None
