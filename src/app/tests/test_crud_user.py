from sqlalchemy.orm import Session

from app import crud
from app.models import User
from app.schemas import UserCreate, UserUpdate
from app.tests.utils import random_email, random_lower_string
from core import verify_password


class TestCRUDUser:
    def test_get_by_email(self, db: Session, normal_user: User):
        # GIVEN
        user, _ = normal_user

        # WHEN
        get_user = crud.user.get_by_email(db, email=user.email)

        # THEN
        assert get_user == user

    def test_get_by_email_not_found(self, db: Session):
        # GIVEN
        email = "random@email.com"

        # WHEN
        user = crud.user.get_by_email(db, email=email)

        # THEN
        assert user is None

    def test_create_user(self, db: Session):
        # GIVEN
        email = random_email()
        password = random_lower_string()
        user = UserCreate(email=email, password=password, full_name=random_lower_string())

        # WHEN
        user_obj = crud.user.create(db, obj=user)

        # THEN
        assert user_obj is not None
        assert user_obj.email == email
        assert hasattr(user_obj, "hashed_password")

    def test_authenticate_user(self, db: Session):
        # GIVEN
        email = random_email()
        password = random_lower_string()
        user = UserCreate(email=email, password=password, full_name=random_lower_string())
        user_obj = crud.user.create(db, obj=user)

        # WHEN
        authenticated_user = crud.user.authenticate(db, email=email, password=password)

        # THEN
        assert authenticated_user
        assert user_obj.email == authenticated_user.email

    def test_authenticate_user_returns_for_invalid_creds(self, db: Session):
        # GIVEN
        email = random_email()
        password = random_lower_string()

        # WHEN
        user = crud.user.authenticate(db, email=email, password=password)

        # THEN
        assert user is None

    def test_user_is_active(self, db: Session, normal_user: User):
        # GIVEN/WHEN/THEN
        normal_user, _ = normal_user
        assert crud.user.is_active(normal_user) is True

    def test_user_is_not_active(self, db: Session, disabled_user: User):
        # GIVEN/WHEN/THEN
        disabled_user, _ = disabled_user
        assert crud.user.is_active(disabled_user) is False

    def test_user_is_admin(self, db: Session, admin_user: User):
        # GIVEN/WHEN/THEN
        admin_user, _ = admin_user
        assert crud.user.is_admin(admin_user) is True

    def test_user_is_not_admin(self, db: Session, normal_user: User):
        # GIVEN/WHEN/THEN
        normal_user, _ = normal_user
        assert crud.user.is_admin(normal_user) is False

    def test_update_user(self, db: Session):
        # GIVEN
        password = random_lower_string()
        email = random_email()
        user = UserCreate(email=email, password=password, full_name=random_lower_string())
        user = crud.user.create(db, obj=user)
        new_password = random_lower_string()
        user_in_update = UserUpdate(password=new_password)

        # WHEN
        crud.user.update(db, db_obj=user, obj=user_in_update)

        # THEN
        user_2 = crud.user.get(db, id=user.id)
        assert user_2
        assert user.email == user_2.email
        assert verify_password(new_password, user_2.hashed_password)