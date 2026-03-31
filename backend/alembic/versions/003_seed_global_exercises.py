"""seed global exercises

Revision ID: 003_ex
Revises: 002_seed
Create Date: 2026-03-31

"""

from typing import Sequence, Union

from alembic import op

revision: str = "003_ex"
down_revision: Union[str, None] = "002_seed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT 'Supino reto', id, NULL FROM muscle_groups
        WHERE name = 'Peito' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = 'Supino reto' AND e.owner_user_id IS NULL
        ) LIMIT 1;
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT 'Remada curvada', id, NULL FROM muscle_groups
        WHERE name = 'Costas' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = 'Remada curvada' AND e.owner_user_id IS NULL
        ) LIMIT 1;
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT 'Agachamento', id, NULL FROM muscle_groups
        WHERE name = 'Pernas' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = 'Agachamento' AND e.owner_user_id IS NULL
        ) LIMIT 1;
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT 'Desenvolvimento', id, NULL FROM muscle_groups
        WHERE name = 'Ombros' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = 'Desenvolvimento' AND e.owner_user_id IS NULL
        ) LIMIT 1;
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT 'Rosca direta', id, NULL FROM muscle_groups
        WHERE name = 'Braços' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = 'Rosca direta' AND e.owner_user_id IS NULL
        ) LIMIT 1;
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT 'Abdominal crunch', id, NULL FROM muscle_groups
        WHERE name = 'Abdómen' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = 'Abdominal crunch' AND e.owner_user_id IS NULL
        ) LIMIT 1;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM exercises WHERE owner_user_id IS NULL AND name IN (
        'Supino reto','Remada curvada','Agachamento','Desenvolvimento','Rosca direta','Abdominal crunch'
        );
        """
    )
