# app/routes.py
from flask import Blueprint, render_template

bp = Blueprint("routes", __name__)

@bp.route("/")
def index():
    # Temporary home page until login is built
    return render_template("index.html")