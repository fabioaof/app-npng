from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import ensure_can_access_user, get_current_user, require_professional
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.models.workout import LinkStatus, ProfessionalStudent
from app.schemas.auth import UserPublic
from app.schemas.professional import (
    StudentAccountCreate,
    StudentLinkCreate,
    StudentProfileUpsert,
    StudentWithProfile,
)
from app.schemas.profile import ProfileRead
from app.api.routers.profiles import profile_to_read

router = APIRouter(prefix="/professional", tags=["professional"])


@router.get("/students", response_model=list[StudentWithProfile])
def list_students(
    request: Request,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> list[StudentWithProfile]:
    links = (
        db.query(ProfessionalStudent)
        .filter(ProfessionalStudent.professional_id == current.id)
        .all()
    )
    out: list[StudentWithProfile] = []
    for link in links:
        u = db.get(User, link.student_id)
        if u is None:
            continue
        prof = db.query(Profile).filter(Profile.user_id == u.id).first()
        pr = profile_to_read(prof, request) if prof else None
        out.append(
            StudentWithProfile(
                user=UserPublic.model_validate(u),
                profile=pr,
                link_status=link.status.value,
            )
        )
    return out


@router.post("/students", response_model=StudentWithProfile, status_code=status.HTTP_201_CREATED)
def link_student(
    request: Request,
    body: StudentLinkCreate,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> StudentWithProfile:
    email = body.student_email.lower()
    student = db.query(User).filter(User.email == email).first()
    if student is None:
        raise HTTPException(status_code=404, detail="Nenhum utilizador com este email. O aluno deve registar-se primeiro.")
    if student.id == current.id:
        raise HTTPException(status_code=400, detail="Não pode adicionar-se a si próprio")
    if student.role != UserRole.user:
        raise HTTPException(status_code=400, detail="Apenas contas de praticante podem ser alunos")
    existing = (
        db.query(ProfessionalStudent)
        .filter(
            ProfessionalStudent.professional_id == current.id,
            ProfessionalStudent.student_id == student.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Aluno já está na sua lista")
    link = ProfessionalStudent(
        professional_id=current.id,
        student_id=student.id,
        status=LinkStatus.active,
    )
    db.add(link)
    db.commit()
    prof = db.query(Profile).filter(Profile.user_id == student.id).first()
    pr = profile_to_read(prof, request) if prof else None
    return StudentWithProfile(
        user=UserPublic.model_validate(student),
        profile=pr,
        link_status=link.status.value,
    )


@router.post(
    "/students/create-account",
    response_model=StudentWithProfile,
    status_code=status.HTTP_201_CREATED,
)
def create_student_account(
    request: Request,
    body: StudentAccountCreate,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> StudentWithProfile:
    email = body.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email já registado")

    student = User(
        email=email,
        hashed_password=get_password_hash(body.password),
        role=UserRole.user,
    )
    db.add(student)
    db.flush()

    prof = Profile(user_id=student.id)
    data = body.model_dump(exclude_unset=True)
    data.pop("email", None)
    data.pop("password", None)
    for k, v in data.items():
        setattr(prof, k, v)
    db.add(prof)
    db.flush()

    link = ProfessionalStudent(
        professional_id=current.id,
        student_id=student.id,
        status=LinkStatus.active,
    )
    db.add(link)
    db.commit()
    db.refresh(student)
    db.refresh(prof)

    return StudentWithProfile(
        user=UserPublic.model_validate(student),
        profile=profile_to_read(prof, request),
        link_status=link.status.value,
    )


@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def unlink_student(
    student_id: int,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> Response:
    link = (
        db.query(ProfessionalStudent)
        .filter(
            ProfessionalStudent.professional_id == current.id,
            ProfessionalStudent.student_id == student_id,
        )
        .first()
    )
    if link is None:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    db.delete(link)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/students/{student_id}/profile", response_model=ProfileRead)
def upsert_student_profile(
    request: Request,
    student_id: int,
    body: StudentProfileUpsert,
    current: Annotated[User, Depends(require_professional)],
    db: Session = Depends(get_db),
) -> ProfileRead:
    ensure_can_access_user(db, current, student_id)
    prof = db.query(Profile).filter(Profile.user_id == student_id).first()
    if prof is None:
        prof = Profile(user_id=student_id)
        db.add(prof)
        db.flush()
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(prof, k, v)
    db.commit()
    db.refresh(prof)
    return profile_to_read(prof, request)
