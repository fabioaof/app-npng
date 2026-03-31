from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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

    @field_validator("sets")
    @classmethod
    def nonempty_sets(cls, v: list[WorkoutSetIn]) -> list[WorkoutSetIn]:
        if not v:
            raise ValueError("Treino deve ter pelo menos um set")
        return v


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
