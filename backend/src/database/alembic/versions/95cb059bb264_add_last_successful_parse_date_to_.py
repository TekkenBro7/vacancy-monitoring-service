"""add last_successful_parse_date to sources

Revision ID: 95cb059bb264
Revises: 5b342eab2468
Create Date: 2026-03-14 13:57:32.010456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95cb059bb264'
down_revision: Union[str, Sequence[str], None] = '5b342eab2468'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
