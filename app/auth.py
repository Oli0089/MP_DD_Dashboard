# app/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, logout_user

# blueprint for authentication routes
auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@auth.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


# redirect to login on logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
