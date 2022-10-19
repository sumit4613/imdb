from typing import Optional

from pydantic import BaseModel
from pydantic.schema import datetime
from pydantic.types import UUID


# Shared properties
class MovieBase(BaseModel):
    name: str
    director: str
    popularity: Optional[float] = None
    imdb_score: float
    genre: list[str]


# Properties to receive on movie creation
class MovieCreate(MovieBase):
    pass


# Properties to receive on movie update
class MovieUpdate(BaseModel):
    name: Optional[str] = None
    director: Optional[str] = None
    popularity: Optional[float] = None
    imdb_score: Optional[float] = None
    genre: Optional[list[str]] = None


# Properties shared by models stored in DB
class MovieInDBBase(MovieBase):
    id: UUID
    # maybe we can share who created the movie
    # but for now show created_by_id
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties to return to client
class Movie(MovieInDBBase):
    pass


# Properties stored in DB
class MovieInDB(MovieInDBBase):
    pass
