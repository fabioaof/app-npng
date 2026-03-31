from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.workout import LinkStatus, ProfessionalStudent

security = HTTPBearer(auto_error=False)


def get_token_payload(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
) -> dict:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[dict, Depends(get_token_payload)],
) -> User:
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    user = db.get(User, int(sub))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilizador não encontrado")
    return user


def require_professional(current: Annotated[User, Depends(get_current_user)]) -> User:
    if current.role != UserRole.professional:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso reservado a profissionais")
    return current


def ensure_can_access_user(
    db: Session,
    actor: User,
    target_user_id: int,
) -> None:
    if actor.id == target_user_id:
        return
    if actor.role != UserRole.professional:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")
    link = (
        db.query(ProfessionalStudent)
        .filter(
            ProfessionalStudent.professional_id == actor.id,
            ProfessionalStudent.student_id == target_user_id,
            ProfessionalStudent.status == LinkStatus.active,
        )
        .first()
    )
    if link is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Aluno não associado a este profissional")
