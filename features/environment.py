from app import create_app, db


def before_scenario(context, scenario):
    # create a fresh app instance for each scenario
    app = create_app()

    # Behave needs CSRF off or it cannot POST to /login
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Ensure tables exist for Behave tests
    with app.app_context():
        db.create_all()

    # Provide a test client to all steps
    context.client = app.test_client()
