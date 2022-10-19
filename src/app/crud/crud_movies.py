from typing import Any, List, Dict, Union

from click import UUID
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, Query

from app.crud.base import CRUDBase
from app.models.movies import Movies
from app.schemas.movies import MovieCreate, MovieUpdate


class CRUDMovie(CRUDBase[Movies, MovieCreate, MovieUpdate]):
    def create_with_owner(
        self, db: Session, *, obj: Union[MovieCreate], created_by_id: int
    ) -> Movies:
        obj_data = jsonable_encoder(obj)
        db_obj = self.model(**obj_data, created_by_id=created_by_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_owner(
        self, db: Session, *, created_by_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Movies]:
        return (
            db.query(self.model)
            .filter(Movies.created_by_id == created_by_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_base_query(self, db: Session) -> Query:
        return db.query(self.model)

    def get_one(self, db: Session) -> Movies:
        return db.query(self.model).first()

    def bulk_insert(self, db: Session, *, objs: List[Union[Movies, MovieCreate]]) -> int:
        objs_data = jsonable_encoder(objs)
        db_objs = [self.model(**obj_data) for obj_data in objs_data]
        db.add_all(db_objs)
        db.commit()
        return len(db_objs)

    def bulk_delete(self, db: Session) -> int:
        return db.query(self.model).delete()

    def filter(self, base_query: Query, *, q: Dict[str, Any]) -> Query:
        """
        Filter movies by query parameters.
        :param base_query:
        :param q:
        :return:
        """
        if "name" in q:
            base_query = base_query.filter(self.model.name.ilike(f"%{q['name']}%"))
        if "genre" in q:
            base_query = base_query.filter(self.model.genre.contains([q["genre"]]))
        if "director" in q:
            base_query = base_query.filter(
                self.model.director.ilike(f"%{q['director']}%")
            )
        if "imdb_score" in q:
            base_query = base_query.filter(self.model.imdb_score == q["imdb_score"])
        if "imdb_score__gte" in q:
            base_query = base_query.filter(
                self.model.imdb_score >= q["imdb_score__gte"]
            )
        if "imdb_score__lte" in q:
            base_query = base_query.filter(
                self.model.imdb_score <= q["imdb_score__lte"]
            )
        if "popularity" in q:
            base_query = base_query.filter(self.model.popularity == q["popularity"])
        if "popularity__gte" in q:
            base_query = base_query.filter(
                self.model.popularity >= q["popularity__gte"]
            )
        if "popularity__lte" in q:
            base_query = base_query.filter(
                self.model.popularity <= q["popularity__lte"]
            )

        return base_query


movie: CRUDMovie = CRUDMovie(Movies)
