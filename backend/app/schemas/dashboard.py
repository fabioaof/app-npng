from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class SummaryCard(BaseModel):
    total_workouts: int
    total_volume_kg: float
    workouts_last_30_days: int


class WeeklyVolumePoint(BaseModel):
    week_start: date
    volume_kg: float


class ExerciseProgressPoint(BaseModel):
    performed_at: date
    max_weight_kg: float
    total_reps: int
