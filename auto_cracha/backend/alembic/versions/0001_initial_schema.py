"""schema inicial - todos os models da Etapa 1

Revision ID: 0001
Revises:
Create Date: 2026-06-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("nome_empresa", sa.String(), nullable=False),
        sa.Column("cnpj", sa.String(), nullable=False, unique=True),
        sa.Column("email_admin", sa.String(), nullable=False, unique=True),
        sa.Column("logo_url", sa.String(), nullable=True),
        sa.Column("cor_primaria", sa.String(), server_default="#0F172A"),
        sa.Column("cor_secundaria", sa.String(), server_default="#FFFFFF"),
        sa.Column("usar_faixa_treinamento", sa.Boolean(), server_default=sa.false()),
        sa.Column("usar_faixa_pcd", sa.Boolean(), server_default=sa.false()),
        sa.Column("faixas_customizadas", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("TRIAL", "ATIVO", "SUSPENSO", "CANCELADO", name="status_tenant"),
            nullable=False,
            server_default="TRIAL",
        ),
        sa.Column("trial_expira_em", sa.DateTime(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "filiais",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("cnpj", sa.String(), nullable=True),
        sa.Column("endereco", sa.String(), nullable=True),
        sa.Column("logo_filial_url", sa.String(), nullable=True),
        sa.Column("logo_grupo_url", sa.String(), nullable=True),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true()),
    )

    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=True),
        sa.Column("filial_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("filiais.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("senha_hash", sa.String(), nullable=False),
        sa.Column(
            "perfil",
            sa.Enum("SUPER_ADMIN", "ADMIN_TENANT", "GESTOR_FILIAL", "VISUALIZADOR", name="perfil_usuario"),
            nullable=False,
        ),
        sa.Column("ativo", sa.Boolean(), server_default=sa.true()),
        sa.Column("convite_token", sa.String(), nullable=True),
        sa.Column("convite_expira_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "colaboradores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filial_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("filiais.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDENTE_LGPD", "ATIVO", "DESLIGADO", "VISITANTE", name="status_colaborador"),
            nullable=False,
            server_default="PENDENTE_LGPD",
        ),
        sa.Column("qr_token", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("cargo", sa.String(), nullable=False),
        sa.Column("cpf", sa.String(), nullable=True),
        sa.Column("cpf_hash", sa.String(), nullable=True),
        sa.Column("celular", sa.String(), nullable=True),
        sa.Column("email_colaborador", sa.String(), nullable=True),
        sa.Column("em_treinamento", sa.Boolean(), server_default=sa.false()),
        sa.Column("pcd", sa.Boolean(), server_default=sa.false()),
        sa.Column("pcd_descricao", sa.String(), nullable=True),
        sa.Column("campos_adicionais", sa.JSON(), nullable=True),
        sa.Column("foto_url", sa.String(), nullable=True),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("exibir_contato_pessoal", sa.Boolean(), server_default=sa.false()),
        sa.Column("contato_emergencia_nome", sa.String(), nullable=True),
        sa.Column("contato_emergencia_tel", sa.String(), nullable=True),
        sa.Column("pin_emergencia_hash", sa.String(), nullable=True),
        sa.Column("dados_medicos_crypto", sa.String(), nullable=True),
        sa.Column("data_desligamento", sa.DateTime(), nullable=True),
        sa.Column("visitante_expira_em", sa.DateTime(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_colaboradores_cpf_hash", "colaboradores", ["cpf_hash"])

    op.create_table(
        "consentimentos_lgpd",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("colaborador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("colaboradores.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDENTE", "AUTORIZADO", "RECUSADO", name="status_consentimento"),
            nullable=False,
            server_default="PENDENTE",
        ),
        sa.Column("link_enviado_em", sa.DateTime(), nullable=True),
        sa.Column("respondido_em", sa.DateTime(), nullable=True),
        sa.Column("ip_resposta", sa.String(), nullable=True),
    )

    op.create_table(
        "assinaturas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("plano", sa.Enum("BRONZE", "PRATA", name="plano_assinatura"), nullable=True),
        sa.Column(
            "status",
            sa.Enum("TRIAL", "ATIVO", "INADIMPLENTE", "CANCELADO", name="status_assinatura"),
            nullable=False,
            server_default="TRIAL",
        ),
        sa.Column("max_colaboradores", sa.Integer(), server_default="5"),
        sa.Column("creditos_pix", sa.Integer(), server_default="0"),
        sa.Column("mp_subscription_id", sa.String(), nullable=True),
        sa.Column("mp_customer_id", sa.String(), nullable=True),
        sa.Column("renovacao_em", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "lotes_impressao",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filial_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("filiais.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_criador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column("nome_lote", sa.String(), nullable=False),
        sa.Column(
            "status_lote",
            sa.Enum(
                "PENDENTE", "GERADO", "IMPRIMINDO", "IMPRESSO", "PARCIALMENTE_IMPRESSO", "ARQUIVADO",
                name="status_lote",
            ),
            nullable=False,
            server_default="PENDENTE",
        ),
        sa.Column("quantidade_total", sa.Integer(), nullable=False),
        sa.Column("quantidade_impressos", sa.Integer(), server_default="0"),
        sa.Column("quantidade_falhados", sa.Integer(), server_default="0"),
        sa.Column("template_id", sa.String(), nullable=False),
        sa.Column(
            "modo_impressao",
            sa.Enum("A4_3X3", "A4_UNITARIO", name="modo_impressao"),
            nullable=False,
            server_default="A4_3X3",
        ),
        sa.Column("pdf_url", sa.String(), nullable=True),
        sa.Column("pdf_tamanho_kb", sa.Integer(), nullable=True),
        sa.Column("pdf_total_paginas", sa.Integer(), nullable=True),
        sa.Column("pdf_hash", sa.String(), nullable=True),
        sa.Column("pago_via", sa.Enum("ASSINATURA", "PIX_AVULSO", name="pago_via"), nullable=True),
        sa.Column("mp_payment_id", sa.String(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("pdf_gerado_em", sa.DateTime(), nullable=True),
        sa.Column("pdf_baixado_em", sa.DateTime(), nullable=True),
        sa.Column("impressao_iniciada_em", sa.DateTime(), nullable=True),
        sa.Column("concluido_em", sa.DateTime(), nullable=True),
        sa.Column("arquivado_em", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "lotes_cracha",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lote_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lotes_impressao.id", ondelete="CASCADE"), nullable=False),
        sa.Column("colaborador_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("colaboradores.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "status_cracha",
            sa.Enum("PENDENTE", "IMPRESSO", "FALHOU", name="status_cracha"),
            nullable=False,
            server_default="PENDENTE",
        ),
        sa.Column("motivo_falha", sa.String(), nullable=True),
        sa.Column("marcado_impresso_em", sa.DateTime(), nullable=True),
        sa.Column("marcado_falha_em", sa.DateTime(), nullable=True),
        sa.Column("posicao_na_pagina", sa.Integer(), nullable=True),
        sa.Column("numero_pagina", sa.Integer(), nullable=True),
        sa.Column("nome_snapshot", sa.String(), nullable=True),
        sa.Column("cargo_snapshot", sa.String(), nullable=True),
        sa.Column("foto_url_snapshot", sa.String(), nullable=True),
        sa.Column("status_lgpd_snapshot", sa.String(), nullable=True),
        sa.Column("filial_nome_snapshot", sa.String(), nullable=True),
        sa.UniqueConstraint("lote_id", "colaborador_id", name="uq_lote_colaborador"),
    )

    op.create_table(
        "historico_lotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lote_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lotes_impressao.id", ondelete="CASCADE"), nullable=False),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True),
        sa.Column(
            "tipo_evento",
            sa.Enum(
                "LOTE_CRIADO", "PDF_GERADO", "PDF_BAIXADO", "CRACHA_IMPRESSO", "CRACHA_FALHOU",
                "LOTE_COMPLETO", "LOTE_PARCIAL", "MINILOTE_CRIADO", "LOTE_ARQUIVADO",
                name="tipo_evento_historico",
            ),
            nullable=False,
        ),
        sa.Column("quantidade_afetada", sa.Integer(), nullable=True),
        sa.Column("descricao", sa.String(), nullable=True),
        sa.Column("estado_json", sa.JSON(), nullable=True),
        sa.Column("ocorrido_em", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "minilotes_reimpressao",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lote_original_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lotes_impressao.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lote_novo_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("lotes_impressao.id", ondelete="SET NULL"), nullable=True),
        sa.Column("crachas_falhados_ids", sa.JSON(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("AGUARDANDO", "NOVO_LOTE_CRIADO", "IMPRESSO", "CANCELADO", name="status_minilote"),
            nullable=False,
            server_default="AGUARDANDO",
        ),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "config_impressao",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("layout_padrao", sa.String(), server_default="A4_3X3"),
        sa.Column("auto_marcar_ao_baixar", sa.Boolean(), server_default=sa.false()),
        sa.Column("exibir_confirmacao", sa.Boolean(), server_default=sa.true()),
        sa.Column("permitir_marcacao_parcial", sa.Boolean(), server_default=sa.true()),
        sa.Column("dias_retencao_lotes", sa.Integer(), server_default="90"),
        sa.Column("notificar_conclusao", sa.Boolean(), server_default=sa.true()),
    )

    op.create_table(
        "config_empresa",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("template_id", sa.String(), server_default="vertical_padrao"),
        sa.Column("setor_sugerido", sa.String(), nullable=True),
        sa.Column("campos_adicionais_config", sa.JSON(), nullable=True),
        sa.Column("redes_sociais", sa.JSON(), nullable=True),
        sa.Column("telefone", sa.String(), nullable=True),
        sa.Column("whatsapp", sa.String(), nullable=True),
        sa.Column("email_empresa", sa.String(), nullable=True),
        sa.Column("endereco_completo", sa.String(), nullable=True),
        sa.Column("nome_fantasia", sa.String(), nullable=True),
        sa.Column("razao_social", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("config_empresa")
    op.drop_table("config_impressao")
    op.drop_table("minilotes_reimpressao")
    op.drop_table("historico_lotes")
    op.drop_table("lotes_cracha")
    op.drop_table("lotes_impressao")
    op.drop_table("assinaturas")
    op.drop_table("consentimentos_lgpd")
    op.drop_index("ix_colaboradores_cpf_hash", table_name="colaboradores")
    op.drop_table("colaboradores")
    op.drop_table("usuarios")
    op.drop_table("filiais")
    op.drop_table("tenants")

    for enum_name in (
        "status_minilote",
        "tipo_evento_historico",
        "status_cracha",
        "pago_via",
        "modo_impressao",
        "status_lote",
        "status_assinatura",
        "plano_assinatura",
        "status_consentimento",
        "status_colaborador",
        "perfil_usuario",
        "status_tenant",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
