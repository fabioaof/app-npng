from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.muscle import Exercise, MuscleGroup
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseRead, MuscleGroupCreate, MuscleGroupRead

router = APIRouter(prefix="/exercises", tags=["exercises"])


def _exercise_read(e: Exercise) -> ExerciseRead:
    mg = e.muscle_group
    return ExerciseRead(
        id=e.id,
        name=e.name,
        muscle_group_id=e.muscle_group_id,
        owner_user_id=e.owner_user_id,
        muscle_group=MuscleGroupRead.model_validate(mg) if mg else None,
    )


@router.get("/muscle-groups", response_model=list[MuscleGroupRead])
def list_muscle_groups(db: Session = Depends(get_db)) -> list[MuscleGroup]:
    return db.query(MuscleGroup).order_by(MuscleGroup.name).all()


@router.post("/muscle-groups", response_model=MuscleGroupRead)
def create_muscle_group(
    body: MuscleGroupCreate,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> MuscleGroup:
    name = body.name.strip()
    existing = db.query(MuscleGroup).filter(MuscleGroup.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Grupo já existe")
    mg = MuscleGroup(name=name)
    db.add(mg)
    db.commit()
    db.refresh(mg)
    return mg


@router.get("", response_model=list[ExerciseRead])
def list_exercises(
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="Filtrar por nome"),
) -> list[Exercise]:
    query = (
        db.query(Exercise)
        .options(joinedload(Exercise.muscle_group))
        .filter((Exercise.owner_user_id.is_(None)) | (Exercise.owner_user_id == current.id))
    )
    if q:
        query = query.filter(Exercise.name.ilike(f"%{q}%"))
    exercises = query.order_by(Exercise.name).all()
    return [_exercise_read(e) for e in exercises]


@router.post("", response_model=ExerciseRead, status_code=status.HTTP_201_CREATED)
def create_exercise(
    body: ExerciseCreate,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ExerciseRead:
    mg = db.get(MuscleGroup, body.muscle_group_id)
    if mg is None:
        raise HTTPException(status_code=400, detail="Grupo muscular inválido")
    ex = Exercise(
        name=body.name.strip(),
        muscle_group_id=body.muscle_group_id,
        owner_user_id=current.id,
    )
    db.add(ex)
    db.commit()
    db.refresh(ex)
    ex = db.query(Exercise).options(joinedload(Exercise.muscle_group)).filter(Exercise.id == ex.id).first()
    return _exercise_read(ex)


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_exercise(
    exercise_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> Response:
    ex = db.get(Exercise, exercise_id)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercício não encontrado")
    if ex.owner_user_id != current.id:
        raise HTTPException(status_code=403, detail="Só pode apagar os seus exercícios")
    db.delete(ex)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
