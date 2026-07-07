import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PlanoAssinatura(str, enum.Enum):
    BRONZE = "BRONZE"
    PRATA = "PRATA"
    OURO = "OURO"


class StatusAssinatura(str, enum.Enum):
    TRIAL = "TRIAL"
    ATIVO = "ATIVO"
    INADIMPLENTE = "INADIMPLENTE"
    CANCELADO = "CANCELADO"


class Assinatura(Base):
    __tablename__ = "assinaturas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    plano: Mapped[Optional[PlanoAssinatura]] = mapped_column(Enum(PlanoAssinatura, name="plano_assinatura"), nullable=True)
    status: Mapped[StatusAssinatura] = mapped_column(
        Enum(StatusAssinatura, name="status_assinatura"), default=StatusAssinatura.TRIAL, nullable=False
    )
    max_colaboradores: Mapped[int] = mapped_column(Integer, default=5)
    creditos_pix: Mapped[int] = mapped_column(Integer, default=0)
    trial_expira_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    mp_payment_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mp_subscription_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    mp_customer_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    renovacao_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
