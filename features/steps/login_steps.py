from behave import given, when, then
from werkzeug.security import generate_password_hash


# given step is already set up in health_step


@when(
    'I submit the login form with username "{username}" '
    'and password "{password}"'
)
def step_submit_login_form(context, username, password):
    # Submit the login form with supplied credentials
    context.response = context.client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


@then('I should see "{text}"')
def step_should_see_text(context, text):
    # Check that the expected message is present in the response
    assert text.encode() in context.response.data

# Test 2, happy path

@given('a user exists with username "{username}" and password "{password}"')
def step_create_user(context, username, password):
    # Create a user through registration route
    email = f"{username}@example.com"
    context.client.post(
        "/register",
        data={
            "username": username,
            "email": email,
            "password": password,
            "confirm_password": password,
        },
        follow_redirects=True,
    )

@when('I log in with username "{username}" and password "{password}"')
def step_login_with_credentials(context, username, password):
    context.response = context.client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True
    )

# Uses the then already setup in this file
