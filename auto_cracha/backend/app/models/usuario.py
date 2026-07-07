import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base


class PerfilUsuario(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN_TENANT = "ADMIN_TENANT"
    GESTOR_FILIAL = "GESTOR_FILIAL"
    VISUALIZADOR = "VISUALIZADOR"


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True
    )
    filial_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id", ondelete="SET NULL"), nullable=True
    )
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    perfil: Mapped[PerfilUsuario] = mapped_column(Enum(PerfilUsuario, name="perfil_usuario"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    convite_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    convite_expira_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    reset_token_expira_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
