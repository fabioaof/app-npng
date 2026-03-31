"""seed muscle groups

Revision ID: 002_seed
Revises: 001_initial
Create Date: 2026-03-31

"""

from typing import Sequence, Union

from alembic import op

revision: str = "002_seed"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO muscle_groups (name) VALUES
        ('Peito'),
        ('Costas'),
        ('Pernas'),
        ('Ombros'),
        ('Braços'),
        ('Abdómen')
        ON CONFLICT (name) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM muscle_groups WHERE name IN (
        'Peito','Costas','Pernas','Ombros','Braços','Abdómen'
        )
        """
    )
