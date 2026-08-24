def test_list_returns_feature_collection(client) -> None:
    response = client.get("/api/places")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 10
    feature = body["features"][0]
    assert feature["type"] == "Feature"
    assert feature["geometry"]["type"] == "Point"


def test_coordinates_are_longitude_latitude_order(client) -> None:
    response = client.get("/api/places/py-saltos-monday")

    body = response.json()
    # Seeded as latitude=-25.561278, longitude=-54.633361 — GeoJSON order
    # puts longitude first. A [lat, lon] swap bug would fail this exact
    # assertion, not just a "two numbers" shape check.
    assert body["geometry"]["coordinates"] == [-54.633361, -25.561278]


def test_filter_by_country(client) -> None:
    response = client.get("/api/places", params={"country": "PY"})

    features = response.json()["features"]
    assert len(features) == 3
    assert all(f["properties"]["country"] == "PY" for f in features)


def test_filter_by_category(client) -> None:
    response = client.get("/api/places", params={"category": "nature"})

    features = response.json()["features"]
    assert len(features) == 3
    assert all(f["properties"]["category"] == "nature" for f in features)


def test_combined_filters(client) -> None:
    response = client.get("/api/places", params={"country": "AR", "category": "landmark"})

    features = response.json()["features"]
    assert len(features) == 1
    assert features[0]["properties"]["id"] == "ar-hito-tres-fronteras"


def test_get_by_id_returns_single_feature(client) -> None:
    response = client.get("/api/places/py-saltos-monday")

    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "Feature"
    assert body["properties"]["city"] == "Presidente Franco"


def test_get_by_id_not_found(client) -> None:
    response = client.get("/api/places/does-not-exist")

    assert response.status_code == 404


def test_health_still_works(client) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_optional_media_fields_default_to_null(client) -> None:
    response = client.get("/api/places/py-saltos-monday")

    properties = response.json()["properties"]
    assert properties["image_url"] is None
    assert properties["website"] is None
    assert properties["address"] is None