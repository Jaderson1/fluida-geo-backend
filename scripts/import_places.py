"""Imports a GeoJSON FeatureCollection of places into the database.

Usage: uv run python scripts/import_places.py path/to/places.geojson

Upserts by id — safe to run twice on the same file, or point at an
edited/regenerated one later. Every feature is validated before anything
is written: one bad feature fails the whole import with a clear message,
instead of leaving some rows loaded and some not.
"""

import json
import logging
import sys
from pathlib import Path

# Running this file directly (`python scripts/import_places.py ...`, the
# documented usage) only puts scripts/ on sys.path, not the project root —
# confirmed by actually running it before this line existed, which failed
# with "No module named 'app'". This makes the direct-path invocation work
# without requiring `python -m scripts.import_places` instead.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.dialects.postgresql import insert

from app.core.logging import setup_logging
from app.db.models.place import Place
from app.db.session import SessionLocal

logger = logging.getLogger("fluida_geo.import_places")

VALID_CATEGORIES = {
    "nature",
    "culture",
    "gastronomy",
    "shopping",
    "landmark",
    "hotel",
    "entertainment",
}
VALID_COUNTRIES = {"BR", "PY", "AR"}

# Loose box around the trinational region. Pure range checks (-180..180 /
# -90..90) can't catch a [lat, lon] swap here specifically, because this
# region's longitudes (~-54) already fall inside the valid latitude range
# — confirmed by actually feeding a swapped pair [-25.5, -54.6] through
# validation before this check existed: it passed silently. This is a
# warning, not a rejection: it's a heuristic on where places usually are,
# not a real boundary, so a legitimate far-away place would be wrongly
# flagged too.
REGION_BOUNDS = {"min_lon": -55.5, "max_lon": -53.5, "min_lat": -26.3, "max_lat": -24.8}


class PlaceValidationError(Exception):
    """A structural or data problem found in the input file, before any write."""


def _validate_feature(feature: object, index: int) -> dict:
    label = f"feature #{index}"
    if not isinstance(feature, dict) or feature.get("type") != "Feature":
        raise PlaceValidationError(f"{label}: type is not 'Feature'")

    geometry = feature.get("geometry") or {}
    if geometry.get("type") != "Point":
        raise PlaceValidationError(f"{label}: geometry.type is not 'Point'")

    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        raise PlaceValidationError(f"{label}: geometry.coordinates must be [longitude, latitude]")

    longitude, latitude = coordinates
    if not isinstance(longitude, (int, float)) or isinstance(longitude, bool) or not (-180 <= longitude <= 180):
        raise PlaceValidationError(f"{label}: invalid longitude {longitude!r}")
    if not isinstance(latitude, (int, float)) or isinstance(latitude, bool) or not (-90 <= latitude <= 90):
        raise PlaceValidationError(f"{label}: invalid latitude {latitude!r}")

    properties = feature.get("properties") or {}

    if not (
        REGION_BOUNDS["min_lon"] <= longitude <= REGION_BOUNDS["max_lon"]
        and REGION_BOUNDS["min_lat"] <= latitude <= REGION_BOUNDS["max_lat"]
    ):
        logger.warning(
            "%s (%s) is outside the expected region (lon=%s, lat=%s) — check for a possible [lat, lon] swap.",
            label,
            properties.get("id"),
            longitude,
            latitude,
        )

    place_id = properties.get("id")
    if not isinstance(place_id, str) or not place_id.strip():
        raise PlaceValidationError(f"{label}: properties.id is missing or empty")

    name = properties.get("name")
    if not isinstance(name, str) or not name.strip():
        raise PlaceValidationError(f"{label} ({place_id}): properties.name is missing or empty")

    country = properties.get("country")
    if country not in VALID_COUNTRIES:
        raise PlaceValidationError(f"{label} ({place_id}): invalid country {country!r}")

    city = properties.get("city")
    if not isinstance(city, str) or not city.strip():
        raise PlaceValidationError(f"{label} ({place_id}): properties.city is missing or empty")

    category = properties.get("category")
    if category not in VALID_CATEGORIES:
        raise PlaceValidationError(f"{label} ({place_id}): invalid category {category!r}")

    return {
        "id": place_id,
        "name": name,
        "country": country,
        "city": city,
        "category": category,
        "description": properties.get("description") or "",
        "longitude": float(longitude),
        "latitude": float(latitude),
        "image_url": properties.get("image_url"),
        "website": properties.get("website"),
        "address": properties.get("address"),
    }


def load_and_validate(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        raise PlaceValidationError("Root object is not a GeoJSON FeatureCollection")

    features = data.get("features")
    if not isinstance(features, list):
        raise PlaceValidationError("FeatureCollection.features is missing or not a list")

    return [_validate_feature(feature, index) for index, feature in enumerate(features)]


def import_places(path: Path, session_factory=SessionLocal) -> int:
    rows = load_and_validate(path)
    if not rows:
        return 0

    with session_factory() as session:
        try:
            stmt = insert(Place).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["id"],
                set_={col: stmt.excluded[col] for col in rows[0] if col != "id"},
            )
            session.execute(stmt)
            session.commit()
        except Exception:
            session.rollback()
            raise

    return len(rows)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/import_places.py path/to/places.geojson", file=sys.stderr)
        raise SystemExit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        raise SystemExit(1)

    setup_logging()
    try:
        count = import_places(path)
    except PlaceValidationError as error:
        logger.error("Import failed: %s", error)
        raise SystemExit(1) from error

    logger.info("Imported %d places from %s", count, path)


if __name__ == "__main__":
    main()