# tests/test_app.py
import pytest
import tempfile
from app import create_app, db
from app.file_discovery import normalise_dd
from app.comparison import compare_csv_files, compare_swh_variants


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
        username="reguser",
        email="reg@example.com",
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


def test_comparison_page_loads(client):
    register_and_login(client)
    response = client.get("/comparison")
    assert response.status_code == 200
    assert b"Run Comparison" in response.data


def test_results_page_loads(client):
    register_and_login(client)
    response = client.get("/results")
    assert response.status_code == 200
    assert b"DD Version" in response.data

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


# Comparison Testing
# =====================================
def test_normalise_dd_formats_version():
    # DD versions should be stored consistently
    assert normalise_dd("141 00") == "141.00"
    assert normalise_dd("140  20") == "140.20"
    assert normalise_dd("13900") == "139.00"


def test_compare_csv_files_passes_when_identical():
    # Matching CSV files should produce a pass result

    csv_content = "A,B,C\n1,2,3"

    # Create two temporary files containing identical data
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file1:
        file1.write(csv_content)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file2:
        file2.write(csv_content)

    # Run the comparison engine
    result = compare_csv_files(file1.name, file2.name)

    # No differences should be found
    assert result["passed"] is True
    assert result["difference_count"] == 0


def test_compare_csv_files_fails_when_values_change():
    # CSV values should be detected if different

    previous_csv = "A,B,C\n1,2,3"
    latest_csv = "A,B,C\n1,9,3"

    # Create two temporary files containing identical data
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file1:
        file1.write(previous_csv)

    with tempfile.NamedTemporaryFile(mode="w", delete=False) as file2:
        file2.write(latest_csv)

    # Run the comparison engine
    result = compare_csv_files(file1.name, file2.name)

    # A changed value should generate a failed comparison
    assert result["passed"] is False
    assert result["difference_count"] == 1


def test_compare_swh_variants_fails_when_variant_missing():
    # A single failed variant should fail the overall SWH result
    comparison_file_pairs = {
        "CA": {"previous": None, "latest": None},
        "CV": {"previous": None, "latest": "file2.csv"}
    }

    result = compare_swh_variants(comparison_file_pairs)

    # Overall result should fail because CV is missing
    assert result["overall_status"] == "failed"

    # The failed variant should be recorded
    assert result["variant_results"]["CA"]["status"] == "missing"
    assert result["variant_results"]["CV"]["status"] == "missing"
