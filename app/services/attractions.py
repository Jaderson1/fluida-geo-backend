from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.attraction import Attraction


def list_attractions(
    session: Session,
    country: str | None = None,
    category: str | None = None,
    city: str | None = None,
) -> list[Attraction]:
    stmt = select(Attraction)
    if country:
        stmt = stmt.where(Attraction.country == country)
    if category:
        stmt = stmt.where(Attraction.category == category)
    if city:
        stmt = stmt.where(Attraction.city == city)
    return list(session.scalars(stmt))


def get_attraction(session: Session, attraction_id: str) -> Attraction | None:
    return session.get(Attraction, attraction_id)
