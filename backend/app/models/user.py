from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    user = "user"
    professional = "professional"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole", native_enum=False, length=32),
        nullable=False,
        default=UserRole.user,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    profile: Mapped[Optional["Profile"]] = relationship(back_populates="user", uselist=False)
    exercises_owned: Mapped[list[Exercise]] = relationship(back_populates="owner")
    workout_sessions: Mapped[list[WorkoutSession]] = relationship(
        foreign_keys="WorkoutSession.user_id",
        back_populates="user",
    )
    sessions_logged: Mapped[list[WorkoutSession]] = relationship(
        foreign_keys="WorkoutSession.logged_by_user_id",
        back_populates="logged_by",
    )

    students: Mapped[list[ProfessionalStudent]] = relationship(
        foreign_keys="ProfessionalStudent.professional_id",
        back_populates="professional",
    )
    coaches: Mapped[list[ProfessionalStudent]] = relationship(
        foreign_keys="ProfessionalStudent.student_id",
        back_populates="student",
    )
