from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User


class MuscleGroup(Base):
    __tablename__ = "muscle_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    exercises: Mapped[list[Exercise]] = relationship(back_populates="muscle_group")


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    muscle_group_id: Mapped[int] = mapped_column(ForeignKey("muscle_groups.id", ondelete="RESTRICT"), nullable=False)
    owner_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    muscle_group: Mapped[MuscleGroup] = relationship(back_populates="exercises")
    owner: Mapped[Optional[User]] = relationship(back_populates="exercises_owned")
