import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.session import get_session
from app.main import app
from app.seed import seed

TEST_DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5432/fluida_geo_test"


@pytest.fixture(scope="session")
def test_session_factory():
    engine = create_engine(TEST_DATABASE_URL)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    seed(session_factory=factory)
    yield factory
    engine.dispose()


@pytest.fixture
def client(test_session_factory):
    def override_get_session():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    from fastapi.testclient import TestClient

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
