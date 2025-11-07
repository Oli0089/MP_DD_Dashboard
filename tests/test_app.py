# tests/test_app.py
# Basic  checks using Flask's test client
import pytest, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from app import create_app


@pytest.fixture()
def client():
    # Test client to make fake requests
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


def test_index_renders(client):
    # Ensures the home page ('/') renders successfully
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Buddy Ticket Tracker" in resp.data

def test_login_page_loads(client):
    # Login should return 200
    response = client.get("/login")
    assert response.status_code == 200

def test_register_page_loads(client):
    # Register should return 200
    response = client.get("/register")
    assert response.status_code == 200

def test_admin_requires_login(client):
    #admin page without login should redirect to login page
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_logout_redirects_to_login(client):
    #logout without being logged in should redirect to login page
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
