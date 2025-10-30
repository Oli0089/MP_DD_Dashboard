# app/__init__.py
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    # uptime probe
    @app.get("/health")            
    def health():
        return jsonify(status="healthy"), 200

    return app