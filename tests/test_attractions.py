def test_list_returns_all_ten(client) -> None:
    response = client.get("/api/attractions")

    assert response.status_code == 200
    assert len(response.json()) == 10


def test_filter_by_country(client) -> None:
    response = client.get("/api/attractions", params={"country": "PY"})

    body = response.json()
    assert len(body) == 3
    assert all(item["country"] == "PY" for item in body)


def test_filter_by_category(client) -> None:
    response = client.get("/api/attractions", params={"category": "nature"})

    body = response.json()
    assert len(body) == 3
    assert all(item["category"] == "nature" for item in body)


def test_combined_filters(client) -> None:
    response = client.get("/api/attractions", params={"country": "AR", "category": "landmark"})

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == "ar-hito-tres-fronteras"


def test_saltos_del_monday_belongs_to_presidente_franco(client) -> None:
    response = client.get("/api/attractions/py-saltos-monday")

    assert response.status_code == 200
    assert response.json()["city"] == "Presidente Franco"


def test_get_by_id_not_found(client) -> None:
    response = client.get("/api/attractions/does-not-exist")

    assert response.status_code == 404
