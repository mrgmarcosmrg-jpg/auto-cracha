import enum
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.db import Base
from app.core.encryption import CpfCriptografado


class StatusColaborador(str, enum.Enum):
    PENDENTE_LGPD = "PENDENTE_LGPD"
    ATIVO = "ATIVO"
    DESLIGADO = "DESLIGADO"
    VISITANTE = "VISITANTE"


class Colaborador(Base):
    __tablename__ = "colaboradores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    filial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[StatusColaborador] = mapped_column(
        Enum(StatusColaborador, name="status_colaborador"), default=StatusColaborador.PENDENTE_LGPD, nullable=False
    )
    # Imutável: gerado no INSERT, nunca atualizado em nenhum endpoint PUT/PATCH.
    qr_token: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, nullable=False, default=uuid.uuid4)

    # Dados profissionais (RH preenche)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    nome_guerra: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cargo: Mapped[str] = mapped_column(String, nullable=False)
    cpf: Mapped[Optional[str]] = mapped_column(CpfCriptografado, nullable=True)
    cpf_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    celular: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email_colaborador: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    em_treinamento: Mapped[bool] = mapped_column(Boolean, default=False)
    pcd: Mapped[bool] = mapped_column(Boolean, default=False)
    pcd_descricao: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    campos_adicionais: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Dados pessoais (colaborador preenche via link)
    foto_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    data_nascimento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    exibir_contato_pessoal: Mapped[bool] = mapped_column(Boolean, default=False)
    contato_emergencia_nome: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contato_emergencia_tel: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Ficha SOS — dados médicos protegidos por PIN
    pin_emergencia_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    dados_medicos_crypto: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Controle
    data_desligamento: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    visitante_expira_em: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    atualizado_em: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())
