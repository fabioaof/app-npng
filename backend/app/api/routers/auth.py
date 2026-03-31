from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.profile import Profile
from app.models.user import User, UserRole
from app.schemas.auth import Token, UserLogin, UserPublic, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
def register(body: UserRegister, db: Session = Depends(get_db)) -> User:
    if db.query(User).filter(User.email == body.email.lower()).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registado")
    role = UserRole.professional if body.role == "professional" else UserRole.user
    user = User(
        email=body.email.lower(),
        hashed_password=get_password_hash(body.password),
        role=role,
    )
    db.add(user)
    db.flush()
    db.add(Profile(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = create_access_token(
        subject=user.id,
        extra_claims={"role": user.role.value},
    )
    return Token(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current: Annotated[User, Depends(get_current_user)]) -> User:
    return current
