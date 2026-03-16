"""add last_successful_parse_date to sources

Revision ID: 5b342eab2468
Revises: c2fa82cd7aeb
Create Date: 2026-03-14 13:43:13.711104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b342eab2468'
down_revision: Union[str, Sequence[str], None] = 'c2fa82cd7aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
