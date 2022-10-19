import random
import string
from typing import Dict, Tuple, Any, List
from typing import Optional

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud
from app.models import Movies
from app.schemas import MovieCreate
from app.schemas.user import UserCreate
from config import settings


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=32))


def random_email() -> str:
    return f"{random_lower_string()}@{random_lower_string()}.com"


def create_user(db: Session, is_admin: bool, is_active: bool = True):
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string()
    user_obj = UserCreate(username=email, email=email, full_name=full_name, password=password)
    user = crud.user.create(db=db, obj=user_obj, is_admin=is_admin, is_active=is_active)
    return user, password


def get_user_token_headers(db: Session, client: TestClient) -> Dict[str, str]:
    user, password = create_user(db, is_admin=False)
    data = {"username": user.email, "password": password}

    response = client.post(f"{settings.API_V1_STR}/login/", data=data)
    response = response.json()
    auth_token = response["access_token"]
    return {"Authorization": f"Bearer {auth_token}"}


def get_admin_token_headers(db: Session, client: TestClient) -> Dict[str, str]:
    admin_user, password = create_user(db, is_admin=True)
    login_data = {
        "username": admin_user.email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/login/", data=login_data)
    response = response.json()
    auth_token = response["access_token"]
    return {"Authorization": f"Bearer {auth_token}"}


def create_random_movie(
    db: Session,
    *,
    name: Optional[str] = None,
    director: Optional[str] = None,
    popularity: Optional[float] = None,
    imdb_score: Optional[float] = None,
    genre: Optional[List] = None,
    created_by_id: Optional[int] = None,
) -> Movies:
    if created_by_id is None:
        user, _ = create_user(db, is_admin=True)
        created_by_id = user.id

    movie_obj = MovieCreate(
        name=name or random_lower_string(),
        director=director or random_lower_string(),
        popularity=popularity or random.randint(80, 100),
        imdb_score=imdb_score or random.randint(8, 10),
        genre=genre or [random_lower_string(), random_lower_string()],
    )

    return crud.movie.create_with_owner(db=db, obj=movie_obj, created_by_id=created_by_id)


def create_random_movies(db: Session, *, created_by_id: Optional[int] = None, count: int = 5) -> Tuple[int, Any]:
    if created_by_id is None:
        user, _ = create_user(db, is_admin=True)
        created_by_id = user.id

    popularity = [random.randint(80, 100) for _ in range(count)]
    imdb_score = [random.randint(8, 10) for _ in range(count)]
    movie_objs = [
        Movies(
            name=random_lower_string(),
            director=random_lower_string(),
            popularity=float(random.choice(popularity)),
            imdb_score=float(random.choice(imdb_score)),
            genre=[random_lower_string(), random_lower_string()],
            created_by_id=created_by_id,
        )
        for _ in range(count)
    ]

    return crud.movie.bulk_insert(db=db, objs=movie_objs), created_by_id
