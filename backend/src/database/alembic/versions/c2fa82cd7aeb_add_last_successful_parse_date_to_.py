"""add last_successful_parse_date to sources

Revision ID: c2fa82cd7aeb
Revises: b15fcd349243
Create Date: 2026-03-14 13:43:08.852874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2fa82cd7aeb'
down_revision: Union[str, Sequence[str], None] = 'b15fcd349243'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
