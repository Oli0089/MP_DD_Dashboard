from behave import given, when, then
from datetime import datetime, timedelta

@given("a ticket exists that was created 5 days ago")
def step_ticket_old(context):
     # Insert a ticket into the DB thats 5 days old
    from app import db
    from app.models import Ticket, User

    username = "agingtester"

    context.client.post(
        "/register",
        data={
            "username": username,
            "email": f"{username}@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )

    with context.app.app_context():
        user = User.query.filter_by(username=username).first()
        assert user is not None, "User for ageing test not found."

        # Timestamp
        old_date = datetime.utcnow() - timedelta(days=5)

        ticket = Ticket(
            external_ref="AGE-001",
            title="Old ticket",
            created_by_id=user.id,
            created_at=old_date,
        )
        db.session.add(ticket)
        db.session.commit()

        context.ticket_id = ticket.id

@when("I view the ticket board")
def step_view_ticket_board(context):
    context.response = context.client.get("/", follow_redirects=True)

@then('I should see the "danger" indicator')
def step_see_danger_indicator(context):
    html = context.response.data.decode()

    # Check for bootstrap colour class
    assert "danger" in html, "Danger (red) indicator not found."
