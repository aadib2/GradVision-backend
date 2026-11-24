"""add application statement_url

Revision ID: 3a6fbf60ca50
Revises: 7646c13f95a9
Create Date: 2026-11-23 18:40:42.179013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a6fbf60ca50'
down_revision: Union[str, Sequence[str], None] = '7646c13f95a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Note: autogenerate also wants to create `refresh_tokens`, because the initial
# migration never did (the app creates it at startup via create_all). That is
# unrelated to this change, so it is deliberately left out here.


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('applications', sa.Column('statement_url', sa.String(length=2048), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('applications', 'statement_url')
