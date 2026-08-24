from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.place import PlaceFeature, PlaceFeatureCollection
from app.services import places as places_service

router = APIRouter(prefix="/places", tags=["places"])

CountryParam = Literal["BR", "PY", "AR"]
CategoryParam = Literal["nature", "culture", "gastronomy", "shopping", "landmark", "hotel", "entertainment"]


@router.get("", response_model=PlaceFeatureCollection)
def list_places(
    country: CountryParam | None = None,
    category: CategoryParam | None = None,
    city: str | None = None,
    session: Session = Depends(get_session),
) -> PlaceFeatureCollection:
    rows = places_service.list_places(session, country, category, city)
    return PlaceFeatureCollection(features=[PlaceFeature.from_place(row) for row in rows])


@router.get("/{place_id}", response_model=PlaceFeature)
def get_place(place_id: str, session: Session = Depends(get_session)) -> PlaceFeature:
    row = places_service.get_place(session, place_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return PlaceFeature.from_place(row)