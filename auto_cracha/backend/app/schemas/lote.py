import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.lote import ModoImpressao, PagoVia, StatusCracha, StatusLote, TipoEventoHistorico


class CriarLoteRequest(BaseModel):
    nome_lote: str
    colaborador_ids: List[uuid.UUID] = Field(min_length=1)
    filial_id: Optional[uuid.UUID] = None
    modo_impressao: ModoImpressao = ModoImpressao.A4_3X3


class LoteCriadoOut(BaseModel):
    lote_id: uuid.UUID
    quantidade_total: int
    total_paginas: int


class LoteCrachaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    colaborador_id: uuid.UUID
    status_cracha: StatusCracha
    motivo_falha: Optional[str] = None
    posicao_na_pagina: Optional[int] = None
    numero_pagina: Optional[int] = None
    nome_snapshot: Optional[str] = None
    cargo_snapshot: Optional[str] = None
    foto_url_snapshot: Optional[str] = None
    status_lgpd_snapshot: Optional[str] = None
    filial_nome_snapshot: Optional[str] = None


class LoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filial_id: uuid.UUID
    nome_lote: str
    status_lote: StatusLote
    quantidade_total: int
    quantidade_impressos: int
    quantidade_falhados: int
    template_id: str
    modo_impressao: ModoImpressao
    pdf_url: Optional[str] = None
    pdf_total_paginas: Optional[int] = None
    pdf_tamanho_kb: Optional[int] = None
    pago_via: Optional[PagoVia] = None
    criado_em: datetime
    pdf_gerado_em: Optional[datetime] = None
    concluido_em: Optional[datetime] = None
    arquivado_em: Optional[datetime] = None


class LoteDetalheOut(LoteOut):
    crachas: List[LoteCrachaOut]


class MarcarFalhaRequest(BaseModel):
    motivo_falha: str


class FalhaRegistradaOut(BaseModel):
    minilote_id: uuid.UUID


class HistoricoLoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tipo_evento: TipoEventoHistorico
    quantidade_afetada: Optional[int] = None
    descricao: Optional[str] = None
    ocorrido_em: datetime


class PdfUrlOut(BaseModel):
    pdf_url: str
