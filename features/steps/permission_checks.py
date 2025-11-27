from behave import given, when, then

# Test 1, Unauthenticated user
# =====================================
# given step is already set up in health_step


@when("I visit the admin page")
def step_visit_admin(context):
    # using the same test client as health steps
    context.response = context.client.get("/admin", follow_redirects=False)


@then("I should be redirected to the login page")
def step_redirect_to_login(context):
    # 302 redirect and header should contain /login
    assert context.response.status_code == 302
    assert "/login" in context.response.headers["Location"]


# Test 2, Non-admin user
# =====================================
# Reuses the scenrio 2 for login from login_roles
# Also reuses the admin page step from test 1
# Only change is home page instead of login


@then("I should be redirected to the home page")
def step_redirect_to_home(context):
    assert context.response.status_code in (302, 303)
    location = context.response.headers.get("Location", "")
    assert location == "/" or location.endswith("/")


# Test 3, Admin user
# =====================================
# Reuses logic from py test to make_admin


@given(
    'an admin user exists with username "{username}" '
    'and password "{password}"'
)
def step_admin_user_exists(context, username, password):
    from app import db
    from app.models import User, Role, UserRole

    # Register the user through the normal route
    context.client.post(
        "/register",
        data={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )

    # Promote them to Admin in the database
    with context.app.app_context():
        user = User.query.filter_by(username=username).first()

        admin_role = Role.query.filter_by(name="Admin").first()
        if admin_role is None:
            admin_role = Role(name="Admin")
            db.session.add(admin_role)
            db.session.commit()

        # Link user to Admin role if not already linked
        existing_link = UserRole.query.filter_by(
            user_id=user.id, role_id=admin_role.id
        ).first()
        if existing_link is None:
            db.session.add(UserRole(user_id=user.id, role_id=admin_role.id))
            db.session.commit()
