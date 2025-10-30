# app/routes.py
from flask import Blueprint, render_template


bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    # Temporary home page until login is built
    return render_template("index.html")


@bp.route("/tickets")
def tickets():
    return render_template("tickets.html")


@bp.route("/admin")
def admin():
    return render_template("admin.html")


@bp.route("/login")
def login():
    return render_template("login.html")


@bp.route("/register")
def register():
    return render_template("register.html")
