"""initial_baseline — full schema from current metadata

Revision ID: ab1607c9eb00
Revises:
Create Date: 2026-07-30 20:53:44.261420

Builds the complete schema directly from ``kepin.db.base.Base.metadata``
(``create_all`` with ``checkfirst``), so ``alembic upgrade head`` works on
a fresh database and is a no-op on databases whose schema already matches
the current metadata.
"""
from typing import Sequence, Union

from alembic import op

from kepin.db.base import Base
import kepin.db.models  # noqa: F401  (register all tables on metadata)


# revision identifiers, used by Alembic.
revision: str = 'ab1607c9eb00'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    Base.metadata.create_all(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    """Downgrade schema (drops every table managed by the metadata)."""
    Base.metadata.drop_all(bind=op.get_bind())
