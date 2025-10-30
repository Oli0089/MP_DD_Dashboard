# tests/test_app.py
# Basic  checks using Flask's test client
import pytest
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
