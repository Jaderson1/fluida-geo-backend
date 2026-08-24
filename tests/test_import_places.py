import json

import pytest
from sqlalchemy import delete, select

from app.db.models.place import Place
from scripts.import_places import PlaceValidationError, import_places


@pytest.fixture
def cleanup_test_places(test_session_factory):
    """test_session_factory is session-scoped and shared with test_places.py,
    which asserts exact counts against the seeded 10 rows — a real failure
    seen when these tests first ran: importer test ids leaked in and broke
    those counts. Deletes anything with a "test-import-" id after each test.
    """
    yield
    with test_session_factory() as session:
        session.execute(delete(Place).where(Place.id.like("test-import-%")))
        session.commit()


def write_geojson(tmp_path, features):
    path = tmp_path / "places.geojson"
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    return path


def make_feature(place_id, name="Teste", country="PY", city="Ciudad del Este", category="nature", lon=-54.6, lat=-25.5):
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "id": place_id,
            "name": name,
            "country": country,
            "city": city,
            "category": category,
            "description": "descrição de teste",
        },
    }


def test_import_inserts_new_place(tmp_path, test_session_factory, cleanup_test_places):
    path = write_geojson(tmp_path, [make_feature("test-import-new")])

    count = import_places(path, session_factory=test_session_factory)

    assert count == 1
    with test_session_factory() as session:
        row = session.get(Place, "test-import-new")
        assert row is not None
        assert row.name == "Teste"


def test_import_extracts_longitude_latitude_correctly(tmp_path, test_session_factory, cleanup_test_places):
    path = write_geojson(tmp_path, [make_feature("test-import-coords", lon=-54.633361, lat=-25.561278)])

    import_places(path, session_factory=test_session_factory)

    with test_session_factory() as session:
        row = session.get(Place, "test-import-coords")
        assert row.longitude == -54.633361
        assert row.latitude == -25.561278


def test_import_updates_existing_place(tmp_path, test_session_factory, cleanup_test_places):
    path_v1 = write_geojson(tmp_path, [make_feature("test-import-update", name="Nome original")])
    import_places(path_v1, session_factory=test_session_factory)

    path_v2 = write_geojson(tmp_path, [make_feature("test-import-update", name="Nome atualizado")])
    import_places(path_v2, session_factory=test_session_factory)

    with test_session_factory() as session:
        rows = session.scalars(select(Place).where(Place.id == "test-import-update")).all()
        assert len(rows) == 1
        assert rows[0].name == "Nome atualizado"


def test_import_is_idempotent(tmp_path, test_session_factory, cleanup_test_places):
    path = write_geojson(tmp_path, [make_feature("test-import-idempotent")])

    import_places(path, session_factory=test_session_factory)
    import_places(path, session_factory=test_session_factory)

    with test_session_factory() as session:
        rows = session.scalars(select(Place).where(Place.id == "test-import-idempotent")).all()
        assert len(rows) == 1


def test_import_stores_optional_media_fields(tmp_path, test_session_factory, cleanup_test_places):
    feature = make_feature("test-import-media")
    feature["properties"]["image_url"] = "https://example.com/photo.jpg"
    feature["properties"]["website"] = "https://example.com"
    feature["properties"]["address"] = "Av. Teste, 123"
    path = write_geojson(tmp_path, [feature])

    import_places(path, session_factory=test_session_factory)

    with test_session_factory() as session:
        row = session.get(Place, "test-import-media")
        assert row.image_url == "https://example.com/photo.jpg"
        assert row.website == "https://example.com"
        assert row.address == "Av. Teste, 123"


@pytest.mark.parametrize(
    "payload",
    [
        {"type": "Feature"},
        {"type": "FeatureCollection"},
        {"type": "FeatureCollection", "features": [{"type": "Feature"}]},
        {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": {"type": "Polygon", "coordinates": []}, "properties": {}}],
        },
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-54.6, -25.5]},
                    "properties": {"name": "sem id", "country": "PY", "city": "CDE", "category": "nature"},
                }
            ],
        },
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-54.6, -25.5]},
                    "properties": {"id": "x", "name": "categoria ruim", "country": "PY", "city": "CDE", "category": "invalida"},
                }
            ],
        },
    ],
)
def test_import_rejects_invalid_geojson(tmp_path, test_session_factory, payload):
    path = tmp_path / "invalid.geojson"
    path.write_text(json.dumps(payload))

    with pytest.raises(PlaceValidationError):
        import_places(path, session_factory=test_session_factory)