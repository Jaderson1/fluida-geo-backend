from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.attraction import AttractionRead
from app.services import attractions as attractions_service

router = APIRouter(prefix="/attractions", tags=["attractions"])


@router.get("", response_model=list[AttractionRead])
def list_attractions(
    country: str | None = None,
    category: str | None = None,
    city: str | None = None,
    session: Session = Depends(get_session),
) -> list[AttractionRead]:
    rows = attractions_service.list_attractions(session, country, category, city)
    return [AttractionRead.model_validate(row) for row in rows]


@router.get("/{attraction_id}", response_model=AttractionRead)
def get_attraction(attraction_id: str, session: Session = Depends(get_session)) -> AttractionRead:
    row = attractions_service.get_attraction(session, attraction_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Attraction not found")
    return AttractionRead.model_validate(row)
