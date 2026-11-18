"""init

Revision ID: 3f681fb49383
Revises:
Create Date: 2026-11-16 22:50:57.900510

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "3f681fb49383"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS vector")
