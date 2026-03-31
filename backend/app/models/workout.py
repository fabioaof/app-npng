from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float as SAFloat
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.muscle import Exercise
from app.models.user import User


class LinkStatus(str, enum.Enum):
    active = "active"
    pending = "pending"


class ProfessionalStudent(Base):
    __tablename__ = "professional_students"
    __table_args__ = (UniqueConstraint("professional_id", "student_id", name="uq_professional_student"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[LinkStatus] = mapped_column(
        SAEnum(LinkStatus, name="linkstatus", native_enum=False, length=16),
        default=LinkStatus.active,
        nullable=False,
    )

    professional: Mapped[User] = relationship(
        foreign_keys=[professional_id],
        back_populates="students",
    )
    student: Mapped[User] = relationship(
        foreign_keys=[student_id],
        back_populates="coaches",
    )


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logged_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    user: Mapped[User] = relationship(foreign_keys=[user_id], back_populates="workout_sessions")
    logged_by: Mapped[Optional[User]] = relationship(foreign_keys=[logged_by_user_id], back_populates="sessions_logged")
    sets: Mapped[list[WorkoutSet]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.set_index",
    )


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False)
    set_index: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_kg: Mapped[float] = mapped_column(SAFloat, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    rest_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    session: Mapped[WorkoutSession] = relationship(back_populates="sets")
    exercise: Mapped[Exercise] = relationship()
