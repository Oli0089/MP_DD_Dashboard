# app/__init__.py
from flask import Flask, jsonify
from app import routes


def create_app():
    app = Flask(__name__)

    # register blueprints
    app.register_blueprint(routes.bp)

    @app.get("/health")
    def health():
        return jsonify(status="healthy"), 200

    return app
