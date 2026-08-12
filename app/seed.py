"""Loads the same 10 records currently hardcoded in
frontend/src/data/attractions.ts. Source of truth stays the TS file until
the frontend is switched to fetch from the API; re-run this after editing
that file to keep the two in sync. Idempotent (upsert by id).

Usage: uv run python -m app.seed
"""

from sqlalchemy.dialects.postgresql import insert

from app.db.base import Base
from app.db.models.attraction import Attraction
from app.db.session import SessionLocal, engine

# lat/lon below are geometry.coordinates[1]/[0] from attractions.ts (GeoJSON
# order is [lon, lat]).
ATTRACTIONS: list[dict] = [
    {
        "id": "br-cataratas",
        "name": "Cataratas do Iguaçu (lado brasileiro)",
        "country": "BR",
        "city": "Foz do Iguaçu",
        "category": "nature",
        "description": "Trilha e mirantes do Parque Nacional do Iguaçu com vista panorâmica das quedas.",
        "latitude": -25.6953,
        "longitude": -54.4367,
    },
    {
        "id": "br-marco-tres-fronteiras",
        "name": "Marco das Três Fronteiras",
        "country": "BR",
        "city": "Foz do Iguaçu",
        "category": "landmark",
        "description": "Obelisco à beira do rio com vista para os pontos equivalentes na Argentina e no Paraguai.",
        "latitude": -25.588278,
        "longitude": -54.590921,
    },
    {
        "id": "br-templo-chen-tien",
        "name": "Templo Budista Chen Tien",
        "country": "BR",
        "city": "Foz do Iguaçu",
        "category": "culture",
        "description": "Maior templo budista da América Latina, aberto à visitação.",
        "latitude": -25.473832,
        "longitude": -54.600031,
    },
    {
        "id": "br-itaipu",
        "name": "Itaipu Binacional — Centro de Recepção de Visitantes",
        "country": "BR",
        "city": "Foz do Iguaçu",
        "category": "landmark",
        "description": "Usina hidrelétrica binacional Brasil-Paraguai; visitas guiadas à estrutura.",
        "latitude": -25.447023,
        "longitude": -54.585165,
    },
    {
        "id": "py-ponte-amizade",
        "name": "Ponte da Amizade (lado paraguaio)",
        "country": "PY",
        "city": "Ciudad del Este",
        "category": "landmark",
        "description": "Ponte sobre o rio Paraná que liga Ciudad del Este a Foz do Iguaçu.",
        "latitude": -25.5169,
        "longitude": -54.6076,
    },
    {
        "id": "py-microcentro",
        "name": "Microcentro de Ciudad del Este",
        "country": "PY",
        "city": "Ciudad del Este",
        "category": "shopping",
        "description": "Região comercial concentrada, conhecida pelo comércio de eletrônicos e importados.",
        "latitude": -25.5119,
        "longitude": -54.6087,
    },
    {
        "id": "py-saltos-monday",
        "name": "Saltos del Monday",
        "country": "PY",
        "city": "Presidente Franco",
        "category": "nature",
        "description": "Quedas d\u2019água menos conhecidas que as do Iguaçu, num afluente do Paraná.",
        "latitude": -25.561278,
        "longitude": -54.633361,
    },
    {
        "id": "ar-cataratas",
        "name": "Cataratas del Iguazú (lado argentino)",
        "country": "AR",
        "city": "Puerto Iguazú",
        "category": "nature",
        "description": "Circuitos Superior e Inferior, incluindo a Garganta do Diabo.",
        "latitude": -25.672,
        "longitude": -54.452,
    },
    {
        "id": "ar-hito-tres-fronteras",
        "name": "Hito Argentino Tres Fronteras",
        "country": "AR",
        "city": "Puerto Iguazú",
        "category": "landmark",
        "description": "Mirante argentino da tríplice fronteira, de frente para o marco brasileiro.",
        "latitude": -25.59476,
        "longitude": -54.59077,
    },
    {
        "id": "ar-costanera",
        "name": "Costanera de Puerto Iguazú",
        "country": "AR",
        "city": "Puerto Iguazú",
        "category": "gastronomy",
        "description": "Orla com restaurantes e vista para o encontro dos rios Iguaçu e Paraná.",
        "latitude": -25.5945,
        "longitude": -54.5866,
    },
]


def seed(session_factory=SessionLocal) -> None:
    with session_factory() as session:
        stmt = insert(Attraction).values(ATTRACTIONS)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={col: stmt.excluded[col] for col in ATTRACTIONS[0] if col != "id"},
        )
        session.execute(stmt)
        session.commit()


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    seed()
    print(f"Seeded {len(ATTRACTIONS)} attractions.")
