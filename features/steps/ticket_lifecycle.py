from behave import given, when

# Helper functions
# =====================================
# Registering and assign role tester
def ensure_tester_user(context, username, password="Password1"):
    # Same as the pytest helper logic
    from app import db
    from app.models import User, Role, UserRole

    with context.app.app_context():
        user = User.query.filter_by(username=username).first()

    if user is None:
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
        with context.app.app_context():
            user = User.query.filter_by(username=username).first()

    # Add Tester role
    with context.app.app_context():
        tester_role = Role.query.filter_by(name="Tester").first()
        if tester_role is None:
            tester_role = Role(name="Tester")
            db.session.add(tester_role)
            db.session.commit()

        link = UserRole.query.filter_by(
            user_id=user.id, role_id=tester_role.id
        ).first()
        if link is None:
            db.session.add(UserRole(user_id=user.id, role_id=tester_role.id))
            db.session.commit()

    context.client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )

def login_user(context, username, password="Password1"):
    # Log in as the user
    context.client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )

# Test 1, Cannot buddy own ticket
# =====================================


@given('I am logged in as tester "{username}"')
def step_logged_in_as_tester(context, username):
    ensure_tester_user(context, username)
    login_user(context, username)


@given("I have created a ticket ready for buddy")
def step_create_ticket_ready_for_buddy(context):
    # Create a ticket in the database
    from app import db
    from app.models import User, Ticket

    with context.app.app_context():
        user = User.query.filter_by(username="owner").first()
        assert user is not None, "User 'owner' was not found in the database."

        # Create a ticket directly in the DB
        ticket = Ticket(
            external_ref="MOTOR-1001",
            title="Owner ticket",
            created_by_id=user.id,
        )
        db.session.add(ticket)
        db.session.commit()

        # Store the id so the buddy step can use it
        context.ticket_id = ticket.id


@when("I try to buddy that ticket")
def step_try_to_buddy_that_ticket(context):
    # Attempt to buddy the ticket
    ticket_id = getattr(context, "ticket_id", None)
    assert ticket_id is not None, "ticket_id missing on context."

    context.response = context.client.post(
        f"/tickets/{ticket_id}/buddied",
        follow_redirects=True,
    )

# then is already present in login_steps to check text

# Test 2, Tickets can be buddied by other users
# =====================================

# given is already set above along with the two ands


@when("I buddy that ticket")
def step_buddy_that_ticket(context):
    # Used when not the owner buddies the ticket
    ticket_id = getattr(context, "ticket_id", None)
    assert ticket_id is not None, "ticket_id missing on context."

    context.response = context.client.post(
        f"/tickets/{ticket_id}/buddied",
        follow_redirects=True,
    )

# then is already present in login_steps to check text
