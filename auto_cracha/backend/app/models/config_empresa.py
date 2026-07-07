import uuid
from typing import Optional

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ConfigEmpresa(Base):
    __tablename__ = "config_empresa"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    template_id: Mapped[str] = mapped_column(String, default="vertical_padrao")
    setor_sugerido: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    campos_adicionais_config: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    redes_sociais: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    telefone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    whatsapp: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_empresa: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    endereco_completo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    nome_fantasia: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    razao_social: Mapped[Optional[str]] = mapped_column(String, nullable=True)
