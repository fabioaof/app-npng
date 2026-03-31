"""seed additional global exercises

Revision ID: 005_more_ex
Revises: 004_birth
Create Date: 2026-03-31

"""

from typing import Sequence, Union

from alembic import op

revision: str = "005_more_ex"
down_revision: Union[str, None] = "004_birth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insert_exercise(name: str, muscle_group: str) -> str:
    return f"""
        INSERT INTO exercises (name, muscle_group_id, owner_user_id)
        SELECT '{name.replace("'", "''")}', id, NULL FROM muscle_groups
        WHERE name = '{muscle_group}' AND NOT EXISTS (
          SELECT 1 FROM exercises e WHERE e.name = '{name.replace("'", "''")}' AND e.owner_user_id IS NULL
        ) LIMIT 1;
    """


def upgrade() -> None:
    exercises: list[tuple[str, str]] = [
        # Peito
        ("Supino inclinado - barra", "Peito"),
        ("Supino reto - barra", "Peito"),
        ("Supino inclinado", "Peito"),
        ("Aberturas - máquina", "Peito"),
        ("Aberturas - halteres", "Peito"),
        # Costas
        ("Puxada aberta - polia", "Costas"),
        ("Puxada fechada - polia", "Costas"),
        ("Remada aberta - polia", "Costas"),
        ("Remada fechada - polia", "Costas"),
        ("Remada unilateral - máquina", "Costas"),
        ("Remada cavalinho", "Costas"),
        # Pernas
        ("Mesa flexora", "Pernas"),
        ("Cadeira extensora - discos", "Pernas"),
        ("Cadeira extensora", "Pernas"),
        # Ombros
        ("Elevação lateral - máquina", "Ombros"),
        # Braços
        ("Bícep martelo", "Braços"),
        ("Bícep direto - halteres", "Braços"),
        ("Bícep banco - barra", "Braços"),
        ("Trícep corda", "Braços"),
        ("Trícep barra V", "Braços"),
    ]
    sql = "".join(_insert_exercise(name, mg) for name, mg in exercises)
    op.execute(sql)


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM exercises WHERE owner_user_id IS NULL AND name IN (
        'Supino inclinado - barra',
        'Supino reto - barra',
        'Supino inclinado',
        'Aberturas - máquina',
        'Aberturas - halteres',
        'Puxada aberta - polia',
        'Puxada fechada - polia',
        'Remada aberta - polia',
        'Remada fechada - polia',
        'Remada unilateral - máquina',
        'Remada cavalinho',
        'Mesa flexora',
        'Cadeira extensora - discos',
        'Cadeira extensora',
        'Elevação lateral - máquina',
        'Bícep martelo',
        'Bícep direto - halteres',
        'Bícep banco - barra',
        'Trícep corda',
        'Trícep barra V'
        );
        """
    )
