import os
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import ensure_can_access_user, get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileRead, ProfileUpdate

ALLOWED_PHOTO = {"image/jpeg", "image/png", "image/webp"}
MAX_PHOTO_BYTES = 5 * 1024 * 1024

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _media_base_url(request: Request) -> str:
    """URL pública da API (https + host) por detrás de Nginx; evita depender só de PUBLIC_BASE_URL."""
    proto = (request.headers.get("x-forwarded-proto") or request.url.scheme or "https").split(",")[0].strip()
    host = (request.headers.get("x-forwarded-host") or request.headers.get("host") or "").split(",")[0].strip()
    if host:
        return f"{proto}://{host}".rstrip("/")
    return str(request.base_url).rstrip("/")


def profile_to_read(p: Profile, request: Request) -> ProfileRead:
    photo_url = None
    if p.photo_path:
        photo_url = f"{_media_base_url(request)}/media/{p.photo_path}"
    return ProfileRead(
        id=p.id,
        user_id=p.user_id,
        full_name=p.full_name,
        birth_date=p.birth_date,
        weight_kg=p.weight_kg,
        height_cm=p.height_cm,
        photo_url=photo_url,
    )


@router.get("/me", response_model=ProfileRead)
def get_my_profile(
    request: Request,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ProfileRead:
    prof = db.query(Profile).filter(Profile.user_id == current.id).first()
    if prof is None:
        prof = Profile(user_id=current.id)
        db.add(prof)
        db.commit()
        db.refresh(prof)
    return profile_to_read(prof, request)


@router.patch("/me", response_model=ProfileRead)
def update_my_profile(
    request: Request,
    body: ProfileUpdate,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ProfileRead:
    prof = db.query(Profile).filter(Profile.user_id == current.id).first()
    if prof is None:
        prof = Profile(user_id=current.id)
        db.add(prof)
        db.flush()
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(prof, k, v)
    db.commit()
    db.refresh(prof)
    return profile_to_read(prof, request)


@router.post("/me/photo", response_model=ProfileRead)
async def upload_my_photo(
    request: Request,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> ProfileRead:
    if file.content_type not in ALLOWED_PHOTO:
        raise HTTPException(status_code=400, detail="Formato permitido: JPEG, PNG ou WebP")
    raw = await file.read()
    if len(raw) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=400, detail="Ficheiro demasiado grande (máx 5MB)")
    ext = Path(file.filename or "").suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".jpg" if file.content_type == "image/jpeg" else ".png"
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    name = f"{current.id}_{uuid.uuid4().hex}{ext}"
    dest = upload_dir / name
    dest.write_bytes(raw)

    prof = db.query(Profile).filter(Profile.user_id == current.id).first()
    if prof is None:
        prof = Profile(user_id=current.id)
        db.add(prof)
        db.flush()
    if prof.photo_path:
        old = upload_dir / prof.photo_path
        if old.exists():
            try:
                os.remove(old)
            except OSError:
                pass
    prof.photo_path = name
    db.commit()
    db.refresh(prof)
    return profile_to_read(prof, request)


@router.get("/user/{user_id}", response_model=ProfileRead)
def get_user_profile(
    request: Request,
    user_id: int,
    current: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> ProfileRead:
    ensure_can_access_user(db, current, user_id)
    prof = db.query(Profile).filter(Profile.user_id == user_id).first()
    if prof is None:
        raise HTTPException(status_code=404, detail="Perfil não encontrado")
    return profile_to_read(prof, request)
