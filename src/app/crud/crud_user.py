from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from core import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj: UserCreate, is_admin: bool = False, is_active: bool = True) -> User:
        db_obj = User(
            email=obj.email,
            hashed_password=get_password_hash(obj.password),
            full_name=obj.full_name,
            is_admin=is_admin,
            is_active=is_active
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        update_data = obj if isinstance(obj, dict) else obj.dict(exclude_unset=True)
        if update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, data=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        if _user := self.get_by_email(db, email=email):
            return _user if verify_password(password, _user.hashed_password) else None
        return None

    def is_active(self, _user: User) -> bool:
        return _user.is_active

    def is_admin(self, _user: User) -> bool:
        return self.is_active(_user) and _user.is_admin


user: CRUDUser = CRUDUser(User)
