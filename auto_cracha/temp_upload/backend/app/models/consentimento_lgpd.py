import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class StatusConsentimento(str, enum.Enum):
    PENDENTE = "PENDENTE"
    AUTORIZADO = "AUTORIZADO"
    RECUSADO = "RECUSADO"


class ConsentimentoLgpd(Base):
    __tablename__ = "consentimentos_lgpd"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    colaborador_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colaboradores.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[StatusConsentimento] = mapped_column(
        Enum(StatusConsentimento, name="status_consentimento"), default=StatusConsentimento.PENDENTE, nullable=False
    )
    link_enviado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    respondido_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ip_resposta: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
