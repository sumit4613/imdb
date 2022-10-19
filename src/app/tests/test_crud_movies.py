import random
import uuid

from sqlalchemy.orm import Session

from app import crud
from app.models import User
from app.schemas import MovieCreate
from app.tests.utils import random_lower_string, create_random_movie


class TestCRUDMovie:
    def test_create_with_owner(self, db: Session, admin_user: User):
        # GIVEN
        name = random_lower_string()
        director = random_lower_string()
        popularity = random.randint(80, 100)
        imdb_score = random.randint(8, 10)
        genre = [random_lower_string(), random_lower_string()]
        user, _ = admin_user
        created_by_id = user.id

        movie_obj = MovieCreate(
            name=name,
            director=director,
            popularity=float(popularity),
            imdb_score=float(imdb_score),
            genre=genre,
        )

        # WHEN
        created_movie = crud.movie.create_with_owner(db, obj=movie_obj, created_by_id=created_by_id)

        # THEN
        assert created_movie
        assert created_movie.name == name
        assert created_movie.director == director
        assert created_movie.popularity == popularity

    def test_get_multi_by_owner_retuns_empty_list_for_invalid_created_by_id(self, db: Session):
        # GIVEN
        invalid_created_by_id = uuid.uuid4()

        # WHEN
        movies = crud.movie.get_multi_by_owner(db, created_by_id=invalid_created_by_id)

        # THEN
        assert movies == []

    def test_get_multi_by_owner(self, db: Session, get_movies):
        # GIVEN
        movie_count, created_by_id = get_movies

        # WHEN
        movies = crud.movie.get_multi_by_owner(db, created_by_id=created_by_id)

        # THEN
        assert len(movies) == movie_count

    def test_filter_with_name(self, db: Session):
        # GIVEN
        create_random_movie(db, name="test movie")
        create_random_movie(db, name="this is a test movie")

        # WHEN
        base_query = crud.movie.get_base_query(db)
        filtered_query = crud.movie.filter(base_query, q={"name": "test"})

        # THEN
        assert len(filtered_query.all()) == 2

        # filter with non-existing name
        filtered_query = crud.movie.filter(base_query, q={"name": "non-existing"})

        assert len(filtered_query.all()) == 0

    def test_filter_with_director(self, db: Session):
        # GIVEN
        create_random_movie(db, director="Christopher Nolan")
        create_random_movie(db, director="Nolan")

        # WHEN
        base_query = crud.movie.get_base_query(db)
        filtered_query = crud.movie.filter(base_query, q={"director": "nolan"})

        # THEN
        assert len(filtered_query.all()) == 2

        # filter with non-existing director
        filtered_query = crud.movie.filter(base_query, q={"director": "who is this"})

        assert len(filtered_query.all()) == 0

    def test_filter_with_genre(self, db: Session):
        # GIVEN
        create_random_movie(db, genre=["adventure", "sci-fi"])
        create_random_movie(db, genre=["action", "sci-fi"])

        # WHEN
        base_query = crud.movie.get_base_query(db)
        filtered_query = crud.movie.filter(base_query, q={"genre": "sci-fi"})

        # THEN
        assert len(filtered_query.all()) == 2

        # filter with different genre
        # GIVEN/WHEN
        filtered_query = crud.movie.filter(base_query, q={"genre": "adventure"})

        # THEN
        assert len(filtered_query.all()) == 1

        # filter with non-existing genre
        # GIVEN/WHEN
        filtered_query = crud.movie.filter(base_query, q={"genre": "wierd"})

        # THEN
        assert len(filtered_query.all()) == 0

    def test_filter_with_imdb_score(self, db: Session):
        # delete old movies
        crud.movie.bulk_delete(db)

        # GIVEN
        create_random_movie(db, imdb_score=8.2)
        create_random_movie(db, imdb_score=9.0)
        create_random_movie(db, imdb_score=9.5)
        create_random_movie(db, imdb_score=9.8)

        # WHEN
        base_query = crud.movie.get_base_query(db)
        filtered_query = crud.movie.filter(base_query, q={"imdb_score": 9.5})

        # THEN
        assert len(filtered_query.all()) == 1

        # filter with non-existing imdb_score
        filtered_query = crud.movie.filter(base_query, q={"imdb_score": 9.9})

        assert len(filtered_query.all()) == 0

        # filter with gte imdb_score
        filtered_query = crud.movie.filter(base_query, q={"imdb_score__gte": 9.0})

        assert len(filtered_query.all()) == 3

        # filter with lte imdb_score
        filtered_query = crud.movie.filter(base_query, q={"imdb_score__lte": 9.0})

        assert len(filtered_query.all()) == 2

    def test_filter_with_popularity(self, db: Session):
        # delete old movies
        crud.movie.bulk_delete(db)

        # GIVEN
        create_random_movie(db, popularity=80.2)
        create_random_movie(db, popularity=90.0)
        create_random_movie(db, popularity=95.5)
        create_random_movie(db, popularity=98.8)

        # WHEN
        base_query = crud.movie.get_base_query(db)
        filtered_query = crud.movie.filter(base_query, q={"popularity": 95.5})

        # THEN
        assert len(filtered_query.all()) == 1

        # filter with non-existing popularity
        filtered_query = crud.movie.filter(base_query, q={"popularity": 99.9})

        assert len(filtered_query.all()) == 0

        # filter with gte popularity
        filtered_query = crud.movie.filter(base_query, q={"popularity__gte": 90.0})

        assert len(filtered_query.all()) == 3

        # filter with lte popularity
        filtered_query = crud.movie.filter(base_query, q={"popularity__lte": 90.0})

        assert len(filtered_query.all()) == 2
