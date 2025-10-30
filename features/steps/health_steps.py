# features/steps/health_steps.py
from behave import given, when, then
from app import create_app

#test instance
@given("the app is initialised")
def step_app_initialised(context):
    app = create_app()
    context.client = app.test_client() 

# Simulates a GET request to /health
@when('I GET "/health"')
def step_get_health(context):
    context.response = context.client.get("/health")

# Verify HTTP 200 and the correct JSON payload
@then('I receive 200 and JSON status "healthy"')
def step_assert_healthy(context):
    assert context.response.status_code == 200
    data = context.response.get_json()
    assert data and data.get("status") == "healthy"