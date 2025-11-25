# tests/test_app.py
import pytest
from app import create_app, db


# Fixtures
# =====================================
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


# Helpers to create a user for tests
# =====================================
def register_user(
        client,
        username="testuser",
        email="test@example.com",
        password="Password1"
):
    return client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )


def register_and_login(
        client,
        username="ticketuser",
        email="ticket@example.com",
        password="Password1"
):
    register_user(client, username=username, email=email, password=password)
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def make_admin(app, username):
    from app.models import User, Role, UserRole
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        admin_role = Role.query.filter_by(name="Admin").first()
        if admin_role is None:
            admin_role = Role(name="Admin")
            db.session.add(admin_role)
            db.session.commit()

        # assign Admin role
        user.roles.append(UserRole(user_id=user.id, role_id=admin_role.id))
        db.session.commit()


def make_tester(app, username):
    from app.models import User, Role, UserRole
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        tester_role = Role.query.filter_by(name="Tester").first()
        if tester_role is None:
            tester_role = Role(name="Tester")
            db.session.add(tester_role)
            db.session.commit()

        # assign tester role
        user.roles.append(UserRole(user_id=user.id, role_id=tester_role.id))
        db.session.commit()


def make_guest(app, username):
    from app.models import User, Role, UserRole
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        tester_role = Role.query.filter_by(name="Guest").first()
        if tester_role is None:
            tester_role = Role(name="Guest")
            db.session.add(tester_role)
            db.session.commit()

        # assign guest role
        user.roles.append(UserRole(user_id=user.id, role_id=tester_role.id))
        db.session.commit()

#Register a tester user, log them in, and create a single ticket
def create_ticket_as_tester(app, client, username, email, external_ref, title):
    from app.models import Ticket

    register_user(client, username=username, email=email, password="Password1")

    make_tester(app, username)

    client.post(
        "/login",
        data={"username": username, "password": "Password1"},
        follow_redirects=True,
    )

    client.post(
        "/tickets",
        data={
            "external_ref": external_ref,
            "title": title,
        },
        follow_redirects=True,
    )

    # Return the created ticket from the DB
    with app.app_context():
        ticket = Ticket.query.filter_by(external_ref=external_ref.upper()).first()
        return ticket

# Basic starting routes & health endpoint
# =====================================
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


# Registration/validation rules
# =====================================
def test_register_rejects_spaces_only_password(client):
    # send a register POST with spaces as a password
    response = client.post(
        "/register",
        data={
            "username": "testspace_user",
            "email": "spaces@example.com",
            "password": "   ",
            "confirm_password": "   ",
        },
        follow_redirects=True,
    )
    # expect the validation message to appear
    assert b"Password cannot be empty or spaces only" in response.data


def test_register_rejects_short_password(client):
    # Password shorter than MIN_PASSWORD_LENGTH should be rejected
    response = client.post(
        "/register",
        data={
            "username": "testshort_user",
            "email": "short@example.com",
            "password": "Pass1",
            "confirm_password": "Pass1",
        },
        follow_redirects=True,
    )
    assert b"Password must be at least" in response.data
    assert b"characters long." in response.data


def test_register_rejects_password_without_letter(client):
    # Password with no letters should be rejected
    response = client.post(
        "/register",
        data={
            "username": "testletter_user",
            "email": "noletter@example.com",
            "password": "12345678",
            "confirm_password": "12345678",
        },
        follow_redirects=True,
    )
    assert (
        b"Password must contain at least one letter and one number."
        in response.data
    )


def test_register_rejects_duplicate_username(client):
    # First registration should succeed
    client.post(
        "/register",
        data={
            "username": "testduplicate_user",
            "email": "first@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )

    # Same username should be rejected
    response = client.post(
        "/register",
        data={
            "username": "testduplicate_user",
            "email": "second@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )
    assert b"Username already exists." in response.data


# Login/logout rules
# =====================================
def test_login_invalid(client):
    resp = client.post(
        "/login",
        data={"username": "nope", "password": "Wrong123"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid username or password" in resp.data


def test_login_valid(client):
    # register user
    client.post(
        "/register",
        data={
            "username": "loginuser",
            "email": "loginuser@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )

    # login
    resp = client.post(
        "/login",
        data={"username": "loginuser", "password": "Password1"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # after login, main page content should be visible
    assert resp.request.path == "/"


def test_logout(client):
    # register and login
    client.post(
        "/register",
        data={
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )
    client.post(
        "/login",
        data={"username": "logoutuser", "password": "Password1"},
        follow_redirects=True,
    )

    # logout
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers.get("Location", "")


# Roles/permissions
# =====================================
def test_admin_page_requires_login(client):
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers.get("Location", "")


def test_admin_can_access_admin_page(app, client):
    # create user
    client.post(
        "/register",
        data={
            "username": "adminuser",
            "email": "admin@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )

    # promote them to admin in the DB
    make_admin(app, username="adminuser")

    client.post(
        "/login",
        data={"username": "adminuser", "password": "Password1"},
        follow_redirects=True,
    )

    # now admin should access admin panel
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code == 200
    assert b"Admin Panel" in resp.data


# Ticket creation/ validation
# =====================================
def test_ticket_create_requires_login(client):
    # Attempt to create a ticket without logging in
    resp = client.post(
        "/tickets",
        data={
            "external_ref": "MOTOR-9999",
            "title": "Should not work",
        },
        follow_redirects=False,
    )

    # Should be redirected to login
    assert resp.status_code in (302, 303)
    assert "/login" in resp.headers.get("Location", "")


def test_ticket_create_valid_data_succeeds(app, client):
    # register/login helper
    register_and_login(
        client,
        username="creator",
        email="creator@example.com",
        password="Password1"
    )

    # Make guest a tester to create a ticketr
    make_tester(app, "creator")

    # Create a valid ticket
    resp = client.post(
        "/tickets",
        data={
            "external_ref": "MOTOR-12345",
            "title": "Unit test ticket"
        },
        follow_redirects=True,
    )

    # Check the request
    assert resp.status_code == 200

    # Check that a ticket exists
    from app.models import Ticket
    with app.app_context():
        count = Ticket.query.count()
        assert count == 1


def test_ticket_create_rejects_invalid_external_ref(app, client):
    register_and_login(
        client,
        username="creator_invalid",
        email="creator_invalid@example.com",
        password="Password1",
    )
    make_tester(app, "creator_invalid")

    # create a ticket with an invalid external ref
    resp = client.post(
        "/tickets",
        data={
            "external_ref": "MTR-123",  # invalid pattern
            "title": "Invalid ref test",
        },
        follow_redirects=True,
    )

    # Form should re-render
    assert resp.status_code == 200

    # Also should not create any tickets
    from app.models import Ticket
    with app.app_context():
        assert Ticket.query.count() == 0


def test_ticket_create_rejects_duplicate_external_ref(app, client):
    register_and_login(
        client,
        username="creator_dup",
        email="creator_dup@example.com",
        password="Password1",
    )
    make_tester(app, "creator_dup")

    # First ticket created
    client.post(
        "/tickets",
        data={
            "external_ref": "MOTOR-777",
            "title": "First ticket",
        },
        follow_redirects=True,
    )

    # Try to create another ticket with the same external_ref
    resp = client.post(
        "/tickets",
        data={
            "external_ref": "MOTOR-777",
            "title": "Duplicate ticket",
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200

    # DB should only have **one** ticket
    from app.models import Ticket
    with app.app_context():
        assert Ticket.query.count() == 1


def test_guest_cannot_create_ticket(app, client):
    register_and_login(
        client,
        username="guestuser",
        email="guest@example.com",
        password="Password1",
    )

    # make user a Guest
    make_guest(app, "guestuser")

    # need to login again to make sure guest is active
    client.post(
        "/login",
        data={"username": "guestuser", "password": "Password1"},
        follow_redirects=True,
    )

    # Attempt to create a ticket as a guest
    resp = client.post(
        "/tickets",
        data={
            "external_ref": "MOTOR-999",
            "title": "Guest ticket",
        },
        follow_redirects=True,
    )

    assert resp.status_code == 200

    # Guest should not have been able to create a ticket
    from app.models import Ticket
    with app.app_context():
        assert Ticket.query.count() == 0


# Ticket lifecycle
# =====================================
def test_user_cannot_buddy_own_ticket(app, client):
    # Create a tester and ticket
    ticket = create_ticket_as_tester(
        app,
        client,
        username="owner",
        email="owner@example.com",
        external_ref="MOTOR-200",
        title="Owner ticket",
    )

    # try to buddy own ticket
    resp = client.post(
        f"/tickets/{ticket.id}/buddied",
        follow_redirects=True,
    )

    assert resp.status_code == 200

    # Ticket should not be buddied
    from app.models import Ticket
    with app.app_context():
        updated = Ticket.query.get(ticket.id)
        assert updated.status == "ready_for_buddy"
        assert updated.buddy_id is None


def test_other_user_can_buddy_ticket(app, client):
    ticket = create_ticket_as_tester(
        app,
        client,
        username="owner2",
        email="owner2@example.com",
        external_ref="MOTOR-201",
        title="Ticket to be buddied",
    )

    # Log out the owner
    client.get("/logout", follow_redirects=True)

    # Register and log in as a different tester who will buddy the ticket
    register_user(
        client,
        username="buddyuser",
        email="buddy@example.com",
        password="Password1",
    )

    make_tester(app, "buddyuser")

    client.post(
        "/login",
        data={"username": "buddyuser", "password": "Password1"},
        follow_redirects=True,
    )

    # Buddy the ticket as the second user
    resp = client.post(
        f"/tickets/{ticket.id}/buddied",
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # Ticket should now be marked as buddied by buddyuser
    from app.models import Ticket, User
    with app.app_context():
        updated = Ticket.query.get(ticket.id)
        buddy = User.query.filter_by(username="buddyuser").first()

        assert updated.status == "buddied"
        assert updated.buddy_id == buddy.id


def test_admin_can_delete_buddied_ticket(app, client):
    ticket = create_ticket_as_tester(
        app,
        client,
        username="owner3",
        email="owner3@example.com",
        external_ref="MOTOR-300",
        title="Ticket to delete",
    )

    # Log out owner
    client.get("/logout", follow_redirects=True)

    # Second tester buddies the ticket
    register_user(
        client,
        username="buddy_for_delete",
        email="buddy_for_delete@example.com",
        password="Password1",
    )

    make_tester(app, "buddy_for_delete")

    client.post(
        "/login",
        data={"username": "buddy_for_delete", "password": "Password1"},
        follow_redirects=True,
    )
    client.post(
        f"/tickets/{ticket.id}/buddied",
        follow_redirects=True,
    )

    # Log out of buddy user
    client.get("/logout", follow_redirects=True)

    # Admin log in
    register_user(
        client,
        username="admin_delete",
        email="admin_delete@example.com",
        password="Password1",
    )

    make_admin(app, "admin_delete")

    client.post(
        "/login",
        data={"username": "admin_delete", "password": "Password1"},
        follow_redirects=True,
    )

    # Admin deletes the buddied ticket
    resp = client.post(
        f"/tickets/{ticket.id}/delete",
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # Check the ticket has been deleted
    from app.models import Ticket
    with app.app_context():
        assert Ticket.query.get(ticket.id) is None


def test_cannot_delete_ticket_if_not_buddied(app, client):
    ticket = create_ticket_as_tester(
        app,
        client,
        username="owner4",
        email="owner4@example.com",
        external_ref="MOTOR-301",
        title="Not buddied yet",
    )

    # Log out owner
    client.get("/logout", follow_redirects=True)

    # Skip the buddy step
    # Admin logs in
    register_user(
        client,
        username="admin_cannot_delete",
        email="admin_cannot_delete@example.com",
        password="Password1",
    )

    make_admin(app, "admin_cannot_delete")

    client.post(
        "/login",
        data={"username": "admin_cannot_delete", "password": "Password1"},
        follow_redirects=True,
    )

    # Try to delete a ticket that is not buddied
    resp = client.post(
        f"/tickets/{ticket.id}/delete",
        follow_redirects=True,
    )
    assert resp.status_code == 200

    # The ticket should still exist
    from app.models import Ticket
    with app.app_context():
        updated = Ticket.query.get(ticket.id)
        assert updated is not None
        assert updated.status == "ready_for_buddy"
