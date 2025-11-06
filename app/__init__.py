# app/__init__.py
import os
from flask import Flask, jsonify
from app import routes
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)


    # to be updated
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

    # database URL
    # set on Render for Postgres
    database_url = os.environ.get("DATABASE_URL")

    # Render reported to sometimes give unexpected URLs
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    if test_config is not None:
        # allow tests to override any config if needed
        app.config.update(test_config)
    elif database_url:
        # deployed Database
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        # local dev SQLite file
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"


    # link database
    db.init_app(app)


    # register blueprints
    app.register_blueprint(routes.bp)


    @app.get("/health")
    def health():
        return jsonify(status="healthy"), 200


    return app
