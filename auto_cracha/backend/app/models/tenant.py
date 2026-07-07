import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class StatusTenant(str, enum.Enum):
    TRIAL = "TRIAL"
    ATIVO = "ATIVO"
    SUSPENSO = "SUSPENSO"
    CANCELADO = "CANCELADO"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_empresa: Mapped[str] = mapped_column(String, nullable=False)
    cnpj: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email_admin: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    logo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    logo_grupo_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cor_primaria: Mapped[str] = mapped_column(String, default="#0F172A")
    cor_secundaria: Mapped[str] = mapped_column(String, default="#FFFFFF")
    usar_faixa_treinamento: Mapped[bool] = mapped_column(Boolean, default=False)
    usar_faixa_pcd: Mapped[bool] = mapped_column(Boolean, default=False)
    faixas_customizadas: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[StatusTenant] = mapped_column(
        Enum(StatusTenant, name="status_tenant"), default=StatusTenant.TRIAL, nullable=False
    )
    trial_expira_em: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
