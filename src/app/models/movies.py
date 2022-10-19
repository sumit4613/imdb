from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Movies(Base):
    __tablename__ = "movies"

    name = Column(String, index=True, nullable=False)
    director = Column(String, nullable=False)
    popularity = Column(Float, nullable=True)
    imdb_score = Column(Float, nullable=False, default=0.0, index=True)
    genre = Column(ARRAY(String), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_by = relationship("User", back_populates="movies")
