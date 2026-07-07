"""adiciona campos de pagamento em assinaturas

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('assinaturas', 'plano',
               existing_type=sa.Enum('BRONZE', 'PRATA', name='plano_assinatura'),
               type_=sa.Enum('BRONZE', 'PRATA', 'OURO', name='plano_assinatura'),
               existing_nullable=True)
    op.add_column(
        "assinaturas",
        sa.Column("trial_expira_em", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "assinaturas",
        sa.Column("mp_payment_id", sa.String(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assinaturas", "mp_payment_id")
    op.drop_column("assinaturas", "trial_expira_em")
    op.alter_column('assinaturas', 'plano',
               existing_type=sa.Enum('BRONZE', 'PRATA', 'OURO', name='plano_assinatura'),
               type_=sa.Enum('BRONZE', 'PRATA', name='plano_assinatura'),
               existing_nullable=True)
