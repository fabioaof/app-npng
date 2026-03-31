from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.api.deps import ensure_can_access_user, get_current_user
from app.db.session import get_db
from app.models.muscle import Exercise
from app.models.user import User, UserRole
from app.models.workout import WorkoutSession, WorkoutSet
from app.schemas.workout import (
    DuplicateSessionBody,
    WorkoutSessionCreate,
    WorkoutSessionRead,
    WorkoutSessionUpdate,
    WorkoutSetRead,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


def _session_read(s: WorkoutSession) -> WorkoutSessionRead:
    sets = [
        WorkoutSetRead(
            id=x.id,
            exercise_id=x.exercise_id,
            set_index=x.set_index,
            weight_kg=x.weight_kg,
            reps=x.reps,
            rest_seconds=x.rest_seconds,
        )
        for x in sorted(s.sets, key=lambda z: (z.exercise_id, z.set_index))
    ]
    return WorkoutSessionRead(
        id=s.id,
        user_id=s.user_id,
        performed_at=s.performed_at,
        title=s.title,
        notes=s.notes,
        logged_by_user_id=s.logged_by_user_id,
        sets=sets,
    )


def _resolve_target_user(
    current: User,
    body_user_id: int | None,
    db: Session,
) -> tuple[int, int | None]:
    """Returns (target_user_id, logged_by_id)."""
    if current.role == UserRole.professional:
        if body_user_id is None:
            raise HTTPException(status_code=400, detail="Indique o aluno (user_id)")
        ensure_can_access_user(db, current, body_user_id)
        return body_user_id, current.id
    if body_user_id is not None and body_user_id != current.id:
        raise HTTPException(status_code=403, detail="Não pode criar treinos para outro utilizador")
    return current.id, None


@router.get("/sessions", response_model=list[WorkoutSessionRead])
def list_sessions(
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    user_id: int | None = Query(None, description="Filtrar por utilizador (profissionais)"),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
) -> list[WorkoutSessionRead]:
    target = current.id if user_id is None else user_id
    if user_id is not None:
        ensure_can_access_user(db, current, user_id)
    q = db.query(WorkoutSession).options(joinedload(WorkoutSession.sets)).filter(WorkoutSession.user_id == target)
    if date_from:
        q = q.filter(WorkoutSession.performed_at >= date_from)
    if date_to:
        q = q.filter(WorkoutSession.performed_at <= date_to)
    sessions = q.order_by(WorkoutSession.performed_at.desc()).all()
    return [_session_read(s) for s in sessions]


@router.post("/sessions", response_model=WorkoutSessionRead, status_code=status.HTTP_201_CREATED)
def create_session(
    body: WorkoutSessionCreate,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkoutSessionRead:
    target_user_id, logged_by = _resolve_target_user(current, body.user_id, db)
    exercise_ids = {x.exercise_id for x in body.sets}
    for eid in exercise_ids:
        ex = db.get(Exercise, eid)
        if ex is None:
            raise HTTPException(status_code=400, detail=f"Exercício {eid} inválido")
        if ex.owner_user_id is not None and ex.owner_user_id not in (current.id, target_user_id):
            raise HTTPException(status_code=400, detail="Exercício não disponível")
    sess = WorkoutSession(
        user_id=target_user_id,
        performed_at=body.performed_at,
        title=body.title,
        notes=body.notes,
        logged_by_user_id=logged_by,
    )
    db.add(sess)
    db.flush()
    for row in body.sets:
        db.add(
            WorkoutSet(
                session_id=sess.id,
                exercise_id=row.exercise_id,
                set_index=row.set_index,
                weight_kg=row.weight_kg,
                reps=row.reps,
                rest_seconds=row.rest_seconds,
            )
        )
    db.commit()
    sess = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.sets))
        .filter(WorkoutSession.id == sess.id)
        .first()
    )
    return _session_read(sess)


@router.get("/sessions/{session_id}", response_model=WorkoutSessionRead)
def get_session(
    session_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkoutSessionRead:
    sess = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.sets))
        .filter(WorkoutSession.id == session_id)
        .first()
    )
    if sess is None:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    ensure_can_access_user(db, current, sess.user_id)
    return _session_read(sess)


@router.patch("/sessions/{session_id}", response_model=WorkoutSessionRead)
def update_session(
    session_id: int,
    body: WorkoutSessionUpdate,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkoutSessionRead:
    sess = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.sets))
        .filter(WorkoutSession.id == session_id)
        .first()
    )
    if sess is None:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    ensure_can_access_user(db, current, sess.user_id)
    if body.performed_at is not None:
        sess.performed_at = body.performed_at
    if body.title is not None:
        sess.title = body.title
    if body.notes is not None:
        sess.notes = body.notes
    if body.sets is not None:
        if not body.sets:
            raise HTTPException(status_code=400, detail="Treino deve ter pelo menos um set")
        exercise_ids = {x.exercise_id for x in body.sets}
        for eid in exercise_ids:
            ex = db.get(Exercise, eid)
            if ex is None:
                raise HTTPException(status_code=400, detail=f"Exercício {eid} inválido")
        for old in list(sess.sets):
            db.delete(old)
        db.flush()
        for row in body.sets:
            db.add(
                WorkoutSet(
                    session_id=sess.id,
                    exercise_id=row.exercise_id,
                    set_index=row.set_index,
                    weight_kg=row.weight_kg,
                    reps=row.reps,
                    rest_seconds=row.rest_seconds,
                )
            )
    db.commit()
    sess = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.sets))
        .filter(WorkoutSession.id == session_id)
        .first()
    )
    return _session_read(sess)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_session(
    session_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> Response:
    sess = db.get(WorkoutSession, session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    ensure_can_access_user(db, current, sess.user_id)
    db.delete(sess)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sessions/{session_id}/duplicate", response_model=WorkoutSessionRead, status_code=status.HTTP_201_CREATED)
def duplicate_session(
    session_id: int,
    body: DuplicateSessionBody,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkoutSessionRead:
    src = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.sets))
        .filter(WorkoutSession.id == session_id)
        .first()
    )
    if src is None:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    ensure_can_access_user(db, current, src.user_id)
    logged_by = current.id if current.role == UserRole.professional and src.user_id != current.id else None
    new_sess = WorkoutSession(
        user_id=src.user_id,
        performed_at=body.performed_at,
        title=src.title,
        notes=src.notes,
        logged_by_user_id=logged_by,
    )
    db.add(new_sess)
    db.flush()
    for row in src.sets:
        db.add(
            WorkoutSet(
                session_id=new_sess.id,
                exercise_id=row.exercise_id,
                set_index=row.set_index,
                weight_kg=row.weight_kg,
                reps=row.reps,
                rest_seconds=row.rest_seconds,
            )
        )
    db.commit()
    new_sess = (
        db.query(WorkoutSession)
        .options(joinedload(WorkoutSession.sets))
        .filter(WorkoutSession.id == new_sess.id)
        .first()
    )
    return _session_read(new_sess)
