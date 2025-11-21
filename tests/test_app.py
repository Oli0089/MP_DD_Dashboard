# tests/test_app.py
import pytest
import warnings

from app import create_app, db

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Fixtures/helpers for all unit tests
#=====================================
@pytest.fixture()
def app():
    # Create a fresh app and database for each test
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            # Uses in-memory database for tests
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        try:
            yield app
        finally:
            db.session.remove()
            db.drop_all()


@pytest.fixture()
def client(app):
    # Test client for making requests
    return app.test_client()

# Basic starting routes & health endpoint
#=====================================

def test_health_endpoint_returns_200_and_json(client):
    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data.get("status") == "healthy"


def test_index_redirects_to_login_when_not_authenticated(client):
    response = client.get("/", follow_redirects=False)

    # login_required should force a redirect to the login page
    assert response.status_code in (302, 303)
    assert "/login" in response.headers.get("Location", "")


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data
