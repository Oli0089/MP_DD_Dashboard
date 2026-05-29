from behave import given, when, then


# Test 1, Authenticated user can access Comparison page
# =====================================
# Registers and logs in as a normal tester, then opens /comparison


@given("I am logged in as a tester")
def step_logged_in_as_tester(context):
    # Register through the normal application route
    context.client.post(
        "/register",
        data={
            "username": "bddtester",
            "email": "bddtester@example.com",
            "password": "Password1",
            "confirm_password": "Password1",
        },
        follow_redirects=True,
    )

    # Login through the normal application route
    context.response = context.client.post(
        "/login",
        data={
            "username": "bddtester",
            "password": "Password1",
        },
        follow_redirects=True,
    )


@when("I open the comparison page")
def step_open_comparison_page(context):
    # Access protected comparison dashboard
    context.response = context.client.get("/comparison")


@then("the comparison page is displayed")
def step_comparison_page_displayed(context):
    assert context.response.status_code == 200
    assert b"Run Comparison" in context.response.data


# Test 2, Authenticated user can access Results page
# =====================================
# Reuses the logged-in tester step from Test 1


@when("I open the results page")
def step_open_results_page(context):
    # Access protected results history page
    context.response = context.client.get("/results")


@then("the results page is displayed")
def step_results_page_displayed(context):
    assert context.response.status_code == 200
    assert b"DD Version" in context.response.data
    assert b"Compared Against" in context.response.data
    assert b"Status" in context.response.data


# Test 3, Stored comparison result updates SWH card
# =====================================
# Uses session state to simulate a completed comparison result


@when('a comparison result is stored for "{swh_key}" as "{status}"')
def step_store_comparison_result(context, swh_key, status):
    # Store tracker state used by comparison dashboard cards
    with context.client.session_transaction() as session:
        session["tracker_statuses"] = {
            swh_key: status,
        }


@then('I should see the SWH status "{status}"')
def step_should_see_swh_status(context, status):
    assert status.encode() in context.response.data


# Test 4, Finalise button unavailable before all SWHs complete
# =====================================
# Confirms users cannot finalise until all SWH cards are complete


@then("the Finalise DD Run button should be disabled")
def step_finalise_button_disabled(context):
    assert context.response.status_code == 200
    assert b"Finalise DD Run" in context.response.data
    assert b"disabled" in context.response.data


# Test 5, Results page shows saved DD history
# =====================================
# Inserts a saved failed DD run so the Results page can display it


@given("a failed DD run exists")
def step_failed_dd_run_exists(context):
    from app import db
    from app.models import DDRun, SWHResult, User

    with context.app.app_context():
        user = User.query.filter_by(username="bddtester").first()

        # Create one failed DD run for the results history table
        dd_run = DDRun(
            dd_version="141.00",
            compared_against="140.20",
            status="Failed",
            user_id=user.id,
        )

        db.session.add(dd_run)
        db.session.flush()

        # Add one failed SWH result with a failed variant
        swh_result = SWHResult(
            dd_run_id=dd_run.id,
            swh_key="acturis_nb",
            swh_name="Acturis NB",
            status="Failed",
            failed_variants="CA",
        )

        db.session.add(swh_result)
        db.session.commit()


@then("I should see the saved DD run history")
def step_saved_dd_history_visible(context):
    assert context.response.status_code == 200
    assert b"141.00" in context.response.data
    assert b"140.20" in context.response.data
    assert b"Failed" in context.response.data
    assert b"View" in context.response.data
    assert b"Acturis NB" in context.response.data
    assert b"CA" in context.response.data
