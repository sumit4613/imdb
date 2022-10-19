from fastapi import status
from fastapi.testclient import TestClient

from app.tests.utils import random_lower_string, random_email
from config import settings
from core import create_access_token


class TestUserEndpoints:
    create_user_url = f"{settings.API_V1_STR}/users/"
    reset_password_url = f"{settings.API_V1_STR}/users/reset-password/"

    def test_create_user_raises_400_is_email_already_exists(self, client: TestClient, normal_user) -> None:
        user, _ = normal_user
        password = random_lower_string()
        data = {"email": user.email, "password": password, "full_name": "test"}
        r = client.post(
            self.create_user_url,
            json=data,
        )
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["detail"] == f"The user with this {user.email=} already exists in the system."

    def test_create_user(self, client: TestClient) -> None:
        email = random_email()
        password = random_lower_string()
        data = {"email": email, "password": password, "full_name": "test"}
        r = client.post(
            self.create_user_url,
            json=data,
        )
        assert r.status_code == status.HTTP_201_CREATED
        assert r.json()["access_token"]
        assert r.json()["token_type"] == "bearer"

    def test_reset_password_raises_400_if_old_password_is_incorrect(
        self, client: TestClient, normal_user, user_token_headers
    ) -> None:
        data = {"old_password": "wrong", "new_password": "new"}
        r = client.post(self.reset_password_url, json=data, headers=user_token_headers)
        assert r.status_code == status.HTTP_400_BAD_REQUEST
        assert r.json()["detail"] == "Incorrect password"

    def test_reset_password(self, client: TestClient, normal_user) -> None:
        user, password = normal_user
        access_token = create_access_token(user.id)
        data = {"old_password": password, "new_password": "new"}
        r = client.post(self.reset_password_url, json=data, headers={"Authorization": f"Bearer {access_token}"})
        assert r.status_code == status.HTTP_202_ACCEPTED
        assert r.json()["msg"] == "Password updated successfully"
