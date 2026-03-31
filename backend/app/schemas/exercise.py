from __future__ import annotations

from pydantic import BaseModel, Field


class MuscleGroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class MuscleGroupRead(MuscleGroupBase):
    id: int

    model_config = {"from_attributes": True}


class MuscleGroupCreate(MuscleGroupBase):
    pass


class ExerciseBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    muscle_group_id: int


class ExerciseRead(ExerciseBase):
    id: int
    owner_user_id: int | None = None
    muscle_group: MuscleGroupRead | None = None

    model_config = {"from_attributes": True}


class ExerciseCreate(ExerciseBase):
    pass
