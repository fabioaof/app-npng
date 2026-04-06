"""workout appointments

Revision ID: 006_appts
Revises: 005_more_ex
Create Date: 2026-04-06

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_appts"
down_revision: Union[str, None] = "005_more_ex"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workout_appointments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("professional_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("linked_session_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["linked_session_id"], ["workout_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["professional_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_workout_appointments_student_id"), "workout_appointments", ["student_id"], unique=False)
    op.create_index(
        op.f("ix_workout_appointments_professional_id"),
        "workout_appointments",
        ["professional_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_workout_appointments_scheduled_for"),
        "workout_appointments",
        ["scheduled_for"],
        unique=False,
    )
    op.create_index(
        "ix_workout_appointments_student_scheduled",
        "workout_appointments",
        ["student_id", "scheduled_for"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_workout_appointments_student_scheduled", table_name="workout_appointments")
    op.drop_index(op.f("ix_workout_appointments_scheduled_for"), table_name="workout_appointments")
    op.drop_index(op.f("ix_workout_appointments_professional_id"), table_name="workout_appointments")
    op.drop_index(op.f("ix_workout_appointments_student_id"), table_name="workout_appointments")
    op.drop_table("workout_appointments")

