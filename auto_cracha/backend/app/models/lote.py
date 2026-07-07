import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class StatusLote(str, enum.Enum):
    PENDENTE = "PENDENTE"
    GERADO = "GERADO"
    IMPRIMINDO = "IMPRIMINDO"
    IMPRESSO = "IMPRESSO"
    PARCIALMENTE_IMPRESSO = "PARCIALMENTE_IMPRESSO"
    ARQUIVADO = "ARQUIVADO"


class ModoImpressao(str, enum.Enum):
    A4_3X3 = "A4_3X3"
    A4_UNITARIO = "A4_UNITARIO"


class PagoVia(str, enum.Enum):
    ASSINATURA = "ASSINATURA"
    PIX_AVULSO = "PIX_AVULSO"


class StatusCracha(str, enum.Enum):
    PENDENTE = "PENDENTE"
    IMPRESSO = "IMPRESSO"
    FALHOU = "FALHOU"


class TipoEventoHistorico(str, enum.Enum):
    LOTE_CRIADO = "LOTE_CRIADO"
    PDF_GERADO = "PDF_GERADO"
    PDF_BAIXADO = "PDF_BAIXADO"
    CRACHA_IMPRESSO = "CRACHA_IMPRESSO"
    CRACHA_FALHOU = "CRACHA_FALHOU"
    LOTE_COMPLETO = "LOTE_COMPLETO"
    LOTE_PARCIAL = "LOTE_PARCIAL"
    MINILOTE_CRIADO = "MINILOTE_CRIADO"
    LOTE_ARQUIVADO = "LOTE_ARQUIVADO"


class StatusMinilote(str, enum.Enum):
    AGUARDANDO = "AGUARDANDO"
    NOVO_LOTE_CRIADO = "NOVO_LOTE_CRIADO"
    IMPRESSO = "IMPRESSO"
    CANCELADO = "CANCELADO"


class LoteImpressao(Base):
    __tablename__ = "lotes_impressao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    filial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id", ondelete="CASCADE"), nullable=False
    )
    usuario_criador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    nome_lote: Mapped[str] = mapped_column(String, nullable=False)
    status_lote: Mapped[StatusLote] = mapped_column(
        Enum(StatusLote, name="status_lote"), default=StatusLote.PENDENTE, nullable=False
    )
    quantidade_total: Mapped[int] = mapped_column(Integer, nullable=False)
    quantidade_impressos: Mapped[int] = mapped_column(Integer, default=0)
    quantidade_falhados: Mapped[int] = mapped_column(Integer, default=0)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    modo_impressao: Mapped[ModoImpressao] = mapped_column(
        Enum(ModoImpressao, name="modo_impressao"), default=ModoImpressao.A4_3X3, nullable=False
    )
    pdf_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pdf_tamanho_kb: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pdf_total_paginas: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pdf_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pago_via: Mapped[Optional[PagoVia]] = mapped_column(Enum(PagoVia, name="pago_via"), nullable=True)
    mp_payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    pdf_gerado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    pdf_baixado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    impressao_iniciada_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    concluido_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    arquivado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class LoteCracha(Base):
    __tablename__ = "lotes_cracha"
    __table_args__ = (UniqueConstraint("lote_id", "colaborador_id", name="uq_lote_colaborador"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lotes_impressao.id", ondelete="CASCADE"), nullable=False
    )
    colaborador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colaboradores.id", ondelete="CASCADE"), nullable=False
    )
    status_cracha: Mapped[StatusCracha] = mapped_column(
        Enum(StatusCracha, name="status_cracha"), default=StatusCracha.PENDENTE, nullable=False
    )
    motivo_falha: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    marcado_impresso_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    marcado_falha_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    posicao_na_pagina: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    numero_pagina: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Snapshot congelado no momento da criação do lote
    nome_snapshot: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cargo_snapshot: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    foto_url_snapshot: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status_lgpd_snapshot: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    filial_nome_snapshot: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class HistoricoLote(Base):
    __tablename__ = "historico_lotes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lote_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lotes_impressao.id", ondelete="CASCADE"), nullable=False
    )
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    tipo_evento: Mapped[TipoEventoHistorico] = mapped_column(
        Enum(TipoEventoHistorico, name="tipo_evento_historico"), nullable=False
    )
    quantidade_afetada: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    descricao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    estado_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ocorrido_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MiniloteReimpressao(Base):
    __tablename__ = "minilotes_reimpressao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lote_original_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lotes_impressao.id", ondelete="CASCADE"), nullable=False
    )
    lote_novo_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lotes_impressao.id", ondelete="SET NULL"), nullable=True
    )
    crachas_falhados_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    status: Mapped[StatusMinilote] = mapped_column(
        Enum(StatusMinilote, name="status_minilote"), default=StatusMinilote.AGUARDANDO, nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())


class ConfigImpressao(Base):
    __tablename__ = "config_impressao"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    layout_padrao: Mapped[str] = mapped_column(String, default="A4_3X3")
    auto_marcar_ao_baixar: Mapped[bool] = mapped_column(Boolean, default=False)
    exibir_confirmacao: Mapped[bool] = mapped_column(Boolean, default=True)
    permitir_marcacao_parcial: Mapped[bool] = mapped_column(Boolean, default=True)
    dias_retencao_lotes: Mapped[int] = mapped_column(Integer, default=90)
    notificar_conclusao: Mapped[bool] = mapped_column(Boolean, default=True)
