from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.place import Place


def list_places(
    session: Session,
    country: str | None = None,
    category: str | None = None,
    city: str | None = None,
) -> list[Place]:
    stmt = select(Place)
    if country:
        stmt = stmt.where(Place.country == country)
    if category:
        stmt = stmt.where(Place.category == category)
    if city:
        stmt = stmt.where(Place.city == city)
    return list(session.scalars(stmt))


def get_place(session: Session, place_id: str) -> Place | None:
    return session.get(Place, place_id)