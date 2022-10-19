from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app import crud, models, schemas
from app.api import deps
from core import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    if crud.user.get_by_email(db, email=user.email):
        raise HTTPException(
            status_code=400,
            detail=f"The user with this {user.email=} already exists in the system.",
        )
    user = crud.user.create(db, obj=user)
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.post("/reset-password/", status_code=status.HTTP_202_ACCEPTED)
def reset_password(
    db: Session = Depends(deps.get_db),
    old_password: str = Body(...),
    new_password: str = Body(...),
    user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Only authenticated users can change their password.

    NOTE: This is a very simple implementation of a password reset.
    We can use a more secure method like sending an email with a link to reset the password.
    But I believe that is out of the scope of this project.
    """
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}
