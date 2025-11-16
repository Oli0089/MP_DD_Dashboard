from behave import when, then
from flask import url_for


# given step is already set up in health_step


@when('I submit the login form with username "{username}" and password "{password}"')
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
