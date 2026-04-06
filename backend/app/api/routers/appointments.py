from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from starlette.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import ensure_can_access_user, get_current_user, require_professional
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.workout import AppointmentStatus, WorkoutAppointment, WorkoutSession
from app.schemas.workout import (
    AppointmentConvertBody,
    WorkoutAppointmentCreate,
    WorkoutAppointmentRead,
    WorkoutAppointmentUpdate,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


def _appt_read(a: WorkoutAppointment) -> WorkoutAppointmentRead:
    return WorkoutAppointmentRead(
        id=a.id,
        student_id=a.student_id,
        professional_id=a.professional_id,
        scheduled_for=a.scheduled_for,
        title=a.title,
        notes=a.notes,
        status=a.status,
        linked_session_id=a.linked_session_id,
    )


@router.get("/{appointment_id}", response_model=WorkoutAppointmentRead)
def get_appointment(
    appointment_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkoutAppointmentRead:
    appt = db.get(WorkoutAppointment, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")

    if current.role == UserRole.professional:
        if appt.professional_id != current.id:
            raise HTTPException(status_code=403, detail="Sem permissão")
        ensure_can_access_user(db, current, appt.student_id)
    else:
        if appt.student_id != current.id:
            raise HTTPException(status_code=403, detail="Sem permissão")

    return _appt_read(appt)


@router.get("", response_model=list[WorkoutAppointmentRead])
def list_appointments(
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    user_id: int | None = Query(None, description="Filtrar por utilizador (profissionais)"),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
) -> list[WorkoutAppointmentRead]:
    q = db.query(WorkoutAppointment)

    if current.role == UserRole.professional:
        if user_id is not None:
            ensure_can_access_user(db, current, user_id)
            q = q.filter(WorkoutAppointment.student_id == user_id)
        q = q.filter(WorkoutAppointment.professional_id == current.id)
    else:
        if user_id is not None and user_id != current.id:
            raise HTTPException(status_code=403, detail="Sem permissão")
        q = q.filter(WorkoutAppointment.student_id == current.id)

    if date_from is not None:
        q = q.filter(WorkoutAppointment.scheduled_for >= date_from)
    if date_to is not None:
        q = q.filter(WorkoutAppointment.scheduled_for <= date_to)

    appts = q.order_by(WorkoutAppointment.scheduled_for.asc()).all()
    return [_appt_read(a) for a in appts]


@router.post("", response_model=WorkoutAppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    body: WorkoutAppointmentCreate,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> WorkoutAppointmentRead:
    if body.user_id is None:
        raise HTTPException(status_code=400, detail="Indique o aluno (user_id)")
    ensure_can_access_user(db, current, body.user_id)
    appt = WorkoutAppointment(
        student_id=body.user_id,
        professional_id=current.id,
        scheduled_for=body.scheduled_for,
        title=body.title,
        notes=body.notes,
        status=AppointmentStatus.scheduled,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return _appt_read(appt)


@router.patch("/{appointment_id}", response_model=WorkoutAppointmentRead)
def update_appointment(
    appointment_id: int,
    body: WorkoutAppointmentUpdate,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkoutAppointmentRead:
    appt = db.get(WorkoutAppointment, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")

    if current.role == UserRole.professional:
        if appt.professional_id != current.id:
            raise HTTPException(status_code=403, detail="Sem permissão")
        ensure_can_access_user(db, current, appt.student_id)
    else:
        if appt.student_id != current.id:
            raise HTTPException(status_code=403, detail="Sem permissão")

    data = body.model_dump(exclude_unset=True)
    if "status" in data and data["status"] == AppointmentStatus.converted and appt.linked_session_id is None:
        raise HTTPException(status_code=400, detail="Não pode marcar como convertido sem treino associado")
    for k, v in data.items():
        setattr(appt, k, v)
    db.commit()
    db.refresh(appt)
    return _appt_read(appt)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_appointment(
    appointment_id: int,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> Response:
    appt = db.get(WorkoutAppointment, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")
    if appt.professional_id != current.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    ensure_can_access_user(db, current, appt.student_id)
    db.delete(appt)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{appointment_id}/convert", response_model=WorkoutAppointmentRead)
def convert_appointment(
    appointment_id: int,
    body: AppointmentConvertBody,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> WorkoutAppointmentRead:
    appt = db.get(WorkoutAppointment, appointment_id)
    if appt is None:
        raise HTTPException(status_code=404, detail="Marcação não encontrada")
    if appt.professional_id != current.id:
        raise HTTPException(status_code=403, detail="Sem permissão")
    ensure_can_access_user(db, current, appt.student_id)

    sess = db.get(WorkoutSession, body.session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="Treino não encontrado")
    if sess.user_id != appt.student_id:
        raise HTTPException(status_code=400, detail="Treino não pertence ao aluno da marcação")

    appt.linked_session_id = sess.id
    appt.status = AppointmentStatus.converted
    db.commit()
    db.refresh(appt)
    return _appt_read(appt)

