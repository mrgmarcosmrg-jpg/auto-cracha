from typing import Optional

from pydantic import BaseModel, Field


class PlanoOut(BaseModel):
    id: str
    nome: str
    descricao: str
    preco_reais: float
    max_colaboradores: int
    recursos: list[str]
    destaque: bool


class CriarPreferenciaMercadoPagoRequest(BaseModel):
    plano_id: str = Field(..., description="bronze, prata ou ouro")


class WebhookMercadoPagoBody(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    data: Optional[dict] = None


class CreditosPixRequest(BaseModel):
    quantidade: int = Field(gt=0)


class AssinaturaOut(BaseModel):
    status: str
    plano: str
    max_colaboradores: int
    creditos_pix: int
    trial_expira_em: Optional[str] = None
    mp_payment_id: Optional[str] = None


class CreditosPixOut(BaseModel):
    quantidade: int
    valor_total_reais: float
    status: str
    mensagem: str
