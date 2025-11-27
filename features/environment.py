from app import create_app, db


def before_scenario(context, scenario):
    # Use the same style as pytest, fresh memory DB
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    # Ensure tables exist for Behave tests
    with app.app_context():
        db.create_all()

    # Provide a test client to all steps
    context.app = app
    context.client = app.test_client()
