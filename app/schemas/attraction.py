from pydantic import BaseModel, ConfigDict


class AttractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    country: str
    city: str
    category: str
    description: str
    latitude: float
    longitude: float
