from sqlalchemy.orm import Session

from app import crud, schemas
from app.db import base  # noqa
from app.models import Movies
from config import settings


def init_db(db: Session) -> None:
    # check if we need to create initial data
    movie = crud.movie.get_one(db)
    if not movie:
        # check for user
        user = crud.user.get_by_email(db, email=settings.ADMIN_EMAIL)
        if not user:
            user = schemas.UserCreate(
                full_name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
                is_admin=True,
            )
            user = crud.user.create(db, obj=user)

        # create movies
        movies = parse_fixture_file("imdb.json")
        movie_objs = [
            Movies(
                name=movie["name"],
                director=movie["director"],
                popularity=movie["99popularity"],
                imdb_score=movie["imdb_score"],
                genre=movie["genre"],
                created_by_id=str(user.id),
            )
            for movie in movies
        ]
        count = crud.movie.bulk_insert(db, objs=movie_objs)
        print(f"Created {count} movies")


def parse_fixture_file(file_name):
    import json
    from config import BASE_DIR

    with open(BASE_DIR / "fixtures" / file_name) as f:
        return json.load(f)
