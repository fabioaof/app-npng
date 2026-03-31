from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import ensure_can_access_user, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.workout import WorkoutSession, WorkoutSet
from app.schemas.dashboard import ExerciseProgressPoint, SummaryCard, WeeklyVolumePoint

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _target_user_id(current: User, user_id: int | None) -> int:
    if user_id is None:
        return current.id
    return user_id


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


@router.get("/summary", response_model=SummaryCard)
def summary(
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    user_id: int | None = Query(None),
) -> SummaryCard:
    target = _target_user_id(current, user_id)
    if user_id is not None:
        ensure_can_access_user(db, current, user_id)

    total_workouts = (
        db.query(func.count(WorkoutSession.id)).filter(WorkoutSession.user_id == target).scalar() or 0
    )

    vol = (
        db.query(func.coalesce(func.sum(WorkoutSet.weight_kg * WorkoutSet.reps), 0.0))
        .join(WorkoutSession, WorkoutSet.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == target)
        .scalar()
    )
    total_volume = float(vol or 0)

    since = datetime.now(timezone.utc) - timedelta(days=30)
    last30 = (
        db.query(func.count(WorkoutSession.id))
        .filter(WorkoutSession.user_id == target, WorkoutSession.performed_at >= since)
        .scalar()
        or 0
    )

    return SummaryCard(
        total_workouts=int(total_workouts),
        total_volume_kg=total_volume,
        workouts_last_30_days=int(last30),
    )


@router.get("/volume-weekly", response_model=list[WeeklyVolumePoint])
def volume_weekly(
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    user_id: int | None = Query(None),
    weeks: int = Query(8, ge=1, le=52),
) -> list[WeeklyVolumePoint]:
    target = _target_user_id(current, user_id)
    if user_id is not None:
        ensure_can_access_user(db, current, user_id)

    today = datetime.now(timezone.utc).date()
    start = today - timedelta(weeks=weeks)
    start_dt = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc)

    rows = (
        db.query(WorkoutSession.performed_at, WorkoutSet.weight_kg, WorkoutSet.reps)
        .join(WorkoutSet, WorkoutSet.session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == target, WorkoutSession.performed_at >= start_dt)
        .all()
    )

    by_week: dict[date, float] = defaultdict(float)
    for performed_at, w, r in rows:
        d = performed_at.date() if hasattr(performed_at, "date") else performed_at
        ws = _week_start(d)
        by_week[ws] += float(w) * int(r)

    return [WeeklyVolumePoint(week_start=k, volume_kg=v) for k, v in sorted(by_week.items())]


@router.get("/exercise-progress", response_model=list[ExerciseProgressPoint])
def exercise_progress(
    exercise_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    user_id: int | None = Query(None),
) -> list[ExerciseProgressPoint]:
    target = _target_user_id(current, user_id)
    if user_id is not None:
        ensure_can_access_user(db, current, user_id)

    rows = (
        db.query(
            func.date(WorkoutSession.performed_at).label("d"),
            func.max(WorkoutSet.weight_kg).label("mx"),
            func.sum(WorkoutSet.reps).label("rps"),
        )
        .join(WorkoutSet, WorkoutSet.session_id == WorkoutSession.id)
        .filter(
            WorkoutSession.user_id == target,
            WorkoutSet.exercise_id == exercise_id,
        )
        .group_by("d")
        .order_by("d")
        .all()
    )

    out: list[ExerciseProgressPoint] = []
    for row in rows:
        d = row.d
        if isinstance(d, datetime):
            d = d.date()
        out.append(
            ExerciseProgressPoint(
                performed_at=d,
                max_weight_kg=float(row.mx),
                total_reps=int(row.rps),
            )
        )
    return out
