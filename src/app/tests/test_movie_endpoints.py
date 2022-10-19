import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status

from app import crud
from app.tests.utils import create_user, create_random_movie, create_random_movies
from config import settings
from core import create_access_token


class TestMovieEndpoints:
    movie_url = f"{settings.API_V1_STR}/movies/"

    def test_get_movies(self, client: TestClient, user_token_headers, db: Session) -> None:
        # GIVEN/WHEN
        crud.movie.bulk_delete(db)
        count, _ = create_random_movies(db)
        response = client.get(self.movie_url, headers=user_token_headers)

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == count

    def test_get_movies_respects_limit(self, client: TestClient, user_token_headers, get_movies) -> None:
        # GIVEN/WHEN
        count, _ = get_movies
        limit = 3
        response = client.get(self.movie_url, headers=user_token_headers, params={"limit": limit})

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == limit

    def test_get_movies_respects_offset(self, client: TestClient, db: Session, user_token_headers) -> None:
        # GIVEN/WHEN
        crud.movie.bulk_delete(db)
        count, _ = create_random_movies(db)
        offset = 3
        response = client.get(self.movie_url, headers=user_token_headers, params={"offset": offset})

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == count - offset

    def test_get_movie_raises_404_for_invalid_movie_id(self, client: TestClient, user_token_headers) -> None:
        # GIVEN/WHEN
        movie_id = uuid.uuid4()
        response = client.get(f"{self.movie_url}{movie_id}", headers=user_token_headers)

        # THEN
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Movie not found" in response.json()["detail"]

    def test_get_movie_returns_movie(self, client: TestClient, user_token_headers, get_movie) -> None:
        # GIVEN/WHEN
        movie_id = get_movie.id
        response = client.get(f"{self.movie_url}{movie_id}", headers=user_token_headers)

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == str(movie_id)

    def test_create_movie_raises_401_for_unauthorized_user(self, client: TestClient, user_token_headers) -> None:
        # GIVEN/WHEN
        movie_data = {
            "popularity": 88.0,
            "director": "George Lucas",
            "genre": ["Action", " Adventure", " Fantasy", " Sci-Fi"],
            "imdb_score": 8.8,
            "name": "Star Wars",
        }
        response = client.post(self.movie_url, json=movie_data, headers=user_token_headers)

        # THEN
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not enough permissions" in response.json()["detail"]

    def test_create_movie_raises_422_for_invalid_data(self, client: TestClient, admin_token_headers) -> None:
        # GIVEN/WHEN
        movie_data = {
            "popularity": 88.0,
            "director": "George Lucas",
            "genre": ["Action", " Adventure", " Fantasy", " Sci-Fi"],
            "imdb_score": 8.8,
        }
        response = client.post(self.movie_url, json=movie_data, headers=admin_token_headers)

        # THEN
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "name" in response.json()["detail"][0]["loc"]

    def test_create_movie(self, client: TestClient, admin_token_headers) -> None:
        # GIVEN/WHEN
        movie_data = {
            "popularity": 88.0,
            "director": "George Lucas",
            "genre": ["Action", " Adventure", " Fantasy", " Sci-Fi"],
            "imdb_score": 8.8,
            "name": "Star Wars",
        }
        response = client.post(self.movie_url, json=movie_data, headers=admin_token_headers)

        # THEN
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["name"] == movie_data["name"]
        assert "id" in response.json()
        assert "created_at" in response.json()
        assert "updated_at" in response.json()

    def test_update_movie(self, client: TestClient, db: Session) -> None:
        # GIVEN/WHEN
        user, password = create_user(db, is_admin=True)
        access_token = create_access_token(user.id)

        movie = create_random_movie(db, created_by_id=user.id)
        movie_id = movie.id
        movie_data = {"popularity": 99.0, "name": "Interstellar"}
        response = client.patch(
            f"{self.movie_url}{movie_id}/", json=movie_data, headers={"Authorization": f"Bearer {access_token}"}
        )

        # THEN
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == movie_data["name"]
        assert "id" in response.json()
        assert "created_at" in response.json()
        assert "updated_at" in response.json()

    def test_delete_movie(self, client: TestClient, db: Session) -> None:
        # GIVEN/WHEN
        user, password = create_user(db, is_admin=True)
        access_token = create_access_token(user.id)

        movie = create_random_movie(db, created_by_id=user.id)
        movie_id = movie.id
        response = client.delete(f"{self.movie_url}{movie_id}/", headers={"Authorization": f"Bearer {access_token}"})

        # THEN
        assert response.status_code == status.HTTP_204_NO_CONTENT
