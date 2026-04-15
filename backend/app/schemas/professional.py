from __future__ import annotations

from datetime import date

from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth import UserPublic
from app.schemas.profile import ProfileRead


class StudentLinkCreate(BaseModel):
    student_email: EmailStr


class StudentWithProfile(BaseModel):
    user: UserPublic
    profile: ProfileRead | None = None
    link_status: str

    model_config = {"from_attributes": True}


class StudentProfileUpsert(BaseModel):
    full_name: str | None = Field(None, max_length=200)
    birth_date: date | None = None
    weight_kg: float | None = Field(None, ge=0)
    height_cm: float | None = Field(None, ge=0)


class StudentAccountCreate(StudentProfileUpsert):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
