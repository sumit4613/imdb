from fastapi.testclient import TestClient
from starlette import status

from config import settings


class TestLogin:
    def test_get_access_token_raises_400_for_invalid_creds(self, client: TestClient) -> None:
        login_data = {
            "username": "dummy",
            "password": "dummy@123",
        }
        resp = client.post(f"{settings.API_V1_STR}/login/", data=login_data)
        resp_json = resp.json()
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp_json["detail"] == "Incorrect email or password"

    def test_get_access_token_raises_403_for_inactive_users(self, client: TestClient, disabled_user) -> None:
        user, password = disabled_user
        login_data = {
            "username": user.email,
            "password": password,
        }
        resp = client.post(f"{settings.API_V1_STR}/login/", data=login_data)
        resp_json = resp.json()
        assert resp.status_code == status.HTTP_403_FORBIDDEN
        assert resp_json["detail"] == "Inactive User"

    def test_get_access_token_for_valid_user(self, client: TestClient, normal_user) -> None:
        user, password = normal_user
        login_data = {
            "username": user.email,
            "password": password,
        }
        resp = client.post(f"{settings.API_V1_STR}/login/", data=login_data)
        resp_json = resp.json()
        assert resp.status_code == status.HTTP_200_OK
        assert "access_token" in resp_json
        assert resp_json["access_token"]
        assert resp_json["token_type"] == "bearer"
