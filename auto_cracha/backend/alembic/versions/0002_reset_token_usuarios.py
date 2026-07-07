"""adiciona reset_token e reset_token_expira_em em usuarios

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("reset_token", sa.String(), nullable=True))
    op.add_column("usuarios", sa.Column("reset_token_expira_em", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "reset_token_expira_em")
    op.drop_column("usuarios", "reset_token")
