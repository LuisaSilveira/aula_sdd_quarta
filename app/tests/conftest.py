import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "LISTAS_JSON": str(tmp_path / "listas.json")})
    app.config.update(TESTING=True)

    with app.test_client() as client:
        yield client
