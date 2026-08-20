from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.db.models.place import Place


class PlaceProperties(BaseModel):
    id: str
    name: str
    country: str
    city: str
    category: str
    description: str


class PointGeometry(BaseModel):
    type: Literal["Point"] = "Point"
    # [longitude, latitude] — GeoJSON order, not [lat, lon].
    coordinates: tuple[float, float]


class PlaceFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: PointGeometry
    properties: PlaceProperties

    @classmethod
    def from_place(cls, place: "Place") -> "PlaceFeature":
        return cls(
            geometry=PointGeometry(coordinates=(place.longitude, place.latitude)),
            properties=PlaceProperties(
                id=place.id,
                name=place.name,
                country=place.country,
                city=place.city,
                category=place.category,
                description=place.description,
            ),
        )


class PlaceFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[PlaceFeature]