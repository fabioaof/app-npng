from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
    full_name: str | None = None
    birth_date: date | None = None
    weight_kg: float | None = Field(None, ge=0)
    height_cm: float | None = Field(None, ge=0)


class ProfileRead(ProfileBase):
    id: int
    user_id: int
    photo_url: str | None = None

    model_config = {"from_attributes": True}


class ProfileUpdate(ProfileBase):
    pass
