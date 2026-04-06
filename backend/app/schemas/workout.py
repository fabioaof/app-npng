from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.workout import AppointmentStatus


class WorkoutSetIn(BaseModel):
    exercise_id: int
    set_index: int = Field(ge=0)
    weight_kg: float = Field(ge=0)
    reps: int = Field(ge=0)
    rest_seconds: int | None = Field(None, ge=0)


class WorkoutSetRead(BaseModel):
    id: int
    exercise_id: int
    set_index: int
    weight_kg: float
    reps: int
    rest_seconds: int | None = None

    model_config = {"from_attributes": True}


class WorkoutSessionBase(BaseModel):
    performed_at: datetime
    title: str | None = Field(None, max_length=200)
    notes: str | None = None


class WorkoutSessionCreate(WorkoutSessionBase):
    sets: list[WorkoutSetIn] = Field(default_factory=list)
    user_id: int | None = None


class WorkoutSessionRead(WorkoutSessionBase):
    id: int
    user_id: int
    logged_by_user_id: int | None = None
    sets: list[WorkoutSetRead] = []

    model_config = {"from_attributes": True}


class WorkoutSessionUpdate(BaseModel):
    performed_at: datetime | None = None
    title: str | None = None
    notes: str | None = None
    sets: list[WorkoutSetIn] | None = None


class DuplicateSessionBody(BaseModel):
    performed_at: datetime


class WorkoutAppointmentBase(BaseModel):
    scheduled_for: datetime
    title: str | None = Field(None, max_length=200)
    notes: str | None = None


class WorkoutAppointmentCreate(WorkoutAppointmentBase):
    user_id: int | None = None


class WorkoutAppointmentUpdate(BaseModel):
    scheduled_for: datetime | None = None
    title: str | None = Field(None, max_length=200)
    notes: str | None = None
    status: AppointmentStatus | None = None


class WorkoutAppointmentRead(WorkoutAppointmentBase):
    id: int
    student_id: int
    professional_id: int
    status: AppointmentStatus
    linked_session_id: int | None = None

    model_config = {"from_attributes": True}


class AppointmentConvertBody(BaseModel):
    session_id: int = Field(ge=1)

