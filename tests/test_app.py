# tests/test_app.py
import pytest
import warnings

from app import create_app

warnings.filterwarnings("ignore", category=DeprecationWarning)


@pytest.fixture()
def client():
    # Test client to make fake requests
    app = create_app()
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
    )
    with app.test_client() as c:
        yield c


def test_index_renders(client):
    # Ensures the home page ('/') renders successfully
    resp = client.get("/", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Login" in resp.data


def test_login_page_loads(client):
    # Login should return 200
    response = client.get("/login")
    assert response.status_code == 200


def test_register_page_loads(client):
    # Register should return 200
    response = client.get("/register")
    assert response.status_code == 200


def test_admin_requires_login(client):
    # admin page without login should redirect to login page
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_logout_redirects_to_login(client):
    # logout without being logged in should redirect to login page
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_register_rejects_spaces_only_password(client):
    # send a register POST with spaces as a password
    response = client.post(
        "/register",
        data={
            "username": "test_user_spaces",
            "email": "spaces@example.com",
            "password": "   ",
            "confirm_password": "   ",
        },
        follow_redirects=True,
    )
    # expect the validation message to appear
    assert b"Password cannot be empty or spaces only" in response.data
