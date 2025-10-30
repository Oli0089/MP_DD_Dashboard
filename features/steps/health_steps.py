# features/steps/health_steps.py
from behave import given, when, then
from app import create_app


@given("the app is initialised")
def step_app_initialised(context):
    # Creates a test instance
    app = create_app()
    context.client = app.test_client()


@when('I GET "/health"')
def step_get_health(context):
    # Simulates a GET request to /health
    context.response = context.client.get("/health")


@then('I receive 200 and JSON status "healthy"')
def step_assert_healthy(context):
    # Verify HTTP 200 and the correct JSON payload
    assert context.response.status_code == 200
    data = context.response.get_json()
    assert data and data.get("status") == "healthy"
