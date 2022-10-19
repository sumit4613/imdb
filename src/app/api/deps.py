from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db.session import SessionLocal
from config import settings

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    """Dependency to get a database session."""
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    """Dependency to get current user from token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from e

    if not (user := crud.user.get(db, id=token_data.sub)):
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """Dependency to get current active admin user."""
    if not crud.user.is_admin(current_user):
        raise HTTPException(status_code=401, detail="Not enough permissions")
    return current_user
