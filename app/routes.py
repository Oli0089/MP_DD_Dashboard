# app/routes.py
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models import User, Role, UserRole


bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    # Temporary home page until login is built
    return render_template("index.html")


@bp.route("/tickets")
def tickets():
    return render_template("tickets.html")


# admins only
@bp.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash(
            "You do not have permission to view that page.",
            "danger",
        )
        return redirect(url_for("routes.index"))

    return render_template("admin.html")


# logic to login
@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # get form values
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        # basic check that both fields are filled in
        if not username or not password:
            flash("Please enter both username and password.", "warning")
            return redirect(url_for("routes.login"))

        user = User.query.filter_by(username=username).first()

        # if the user exists and password matches, log them in
        if user and check_password_hash(user.password, password):
            login_user(user)

            # update last_login time
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash("Logged in successfully.", "success")
            return redirect(url_for("routes.index"))

        # otherwise show an error
        flash("Invalid username or password.", "danger")
        return redirect(url_for("routes.login"))

    return render_template("login.html")


# logic to regsiter a new account with checks
@bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # get form values
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic checks
        # fields not empty
        if not username or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("routes.register"))

        # passwords must match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("routes.register"))

        # username must be unique
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "warning")
            return redirect(url_for("routes.register"))

        # email must be unique
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "warning")
            return redirect(url_for("routes.register"))

        # hash the password
        hashed_password = generate_password_hash(password)

        # create the new user
        new_user = User(
            username=username, email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        # all new users start with Guest role
        guest_role = Role.query.filter_by(name="Guest").first()

        # link user to Guest role
        if guest_role:
            link = UserRole(user_id=new_user.id, role_id=guest_role.id)
            db.session.add(link)
            db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("routes.login"))

    return render_template("register.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("routes.login"))
