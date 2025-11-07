from behave import when, then

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
