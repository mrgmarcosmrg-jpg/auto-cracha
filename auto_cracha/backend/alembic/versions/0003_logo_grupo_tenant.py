"""adiciona logo_grupo_url em tenants

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-21

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("tenants", sa.Column("logo_grupo_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("tenants", "logo_grupo_url")
