from typing import Any, List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic.types import UUID
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


####USER ENDPOINTS####
@router.get("/", response_model=List[schemas.Movie])
def get_movies(
    db: Session = Depends(deps.get_db),
    offset: int = 0,
    limit: int = Query(default=100, ge=1, lte=100),
    sstr: Optional[Dict[str, Any]] = None,
    user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    List Movies.

    Authenticated users can only see movie
    """
    results = crud.movie.get_base_query(db)
    if sstr:
        results = crud.movie.filter(base_query=results, q=sstr)
    return results.offset(offset).limit(limit).all()


@router.get("/{id}/", response_model=schemas.Movie)
def get_movie(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    user: models.User = Depends(deps.get_current_user),
) -> Any:
    """
    Get movie by ID.
    """
    if item := crud.movie.get(db=db, id=id):
        return item

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Movie not found for provided {id=}",
    )


####ADMIN ENDPOINTS####
@router.post("/", response_model=schemas.Movie, status_code=status.HTTP_201_CREATED)
def create_movie(
    *,
    db: Session = Depends(deps.get_db),
    movie: schemas.MovieCreate,
    current_user: models.User = Depends(deps.get_current_active_admin_user),
) -> Any:
    """
    Create new Movie.
    """
    if not movie.popularity:
        movie.popularity = movie.imdb_score * 10
    return crud.movie.create_with_owner(db=db, obj=movie, created_by_id=current_user.id)


@router.patch("/{id}/", response_model=schemas.Movie)
def update_movie(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    data: schemas.MovieUpdate,
    current_user: models.User = Depends(deps.get_current_active_admin_user),
) -> Any:
    """
    Update movie.
    """
    movie = crud.movie.get(db=db, id=id)
    if not movie:
        raise HTTPException(
            status_code=404, detail=f"Movie not found for provided {id=}"
        )
    if movie.created_by_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.movie.update(db=db, db_obj=movie, data=data)


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(
    *,
    db: Session = Depends(deps.get_db),
    id: UUID,
    current_user: models.User = Depends(deps.get_current_active_admin_user),
) -> Any:
    """
    Delete Movie.
    """
    movie = crud.movie.get(db=db, id=id)
    if not movie:
        raise HTTPException(
            status_code=404, detail=f"Movie not found for provided {id=}"
        )
    if movie.created_by_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return crud.movie.remove(db=db, id=id)
