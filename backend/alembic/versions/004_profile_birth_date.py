"""profile birth_date replaces age

Revision ID: 004_birth
Revises: 003_ex
Create Date: 2026-03-31

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004_birth"
down_revision: Union[str, None] = "003_ex"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("birth_date", sa.Date(), nullable=True))
    op.drop_column("profiles", "age")


def downgrade() -> None:
    op.add_column("profiles", sa.Column("age", sa.Integer(), nullable=True))
    op.drop_column("profiles", "birth_date")
