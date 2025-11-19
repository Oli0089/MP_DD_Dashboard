# app/routes.py
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role, UserRole, Ticket


bp = Blueprint("routes", __name__)

MIN_PASSWORD_LENGTH = 8


@bp.route("/")
@login_required
def index():
    # Temporary home page until login is built
    return render_template("index.html")


# list and create tickets
@bp.route("/tickets", methods=["GET", "POST"])
@login_required
def tickets():

    if request.method == "POST":
        import re

        # jira reference must match MOTOR-12345 (1 to 5 digits)
        pattern = r"^MOTOR-\d{1,5}$"

        # guest users are read-only, they can still see tickets
        if current_user.is_guest:
            flash("Guest users cannot create tickets.", "warning")
            return redirect(url_for("routes.tickets"))

        # take the Jira reference and short description from the form
        external_ref = request.form.get("external_ref", "").strip()
        title = request.form.get("title", "").strip()

        if not external_ref or not title:
            msg = (
                "Please fill in both the Jira reference and "
                "description."
            )
            flash(msg, "danger")

        # Short description must be under 20 characters
        if len(title) > 20:
            flash("Short description must be under 20 characters", "danger")
            return redirect(url_for("routes.tickets"))

        if not re.match(pattern, external_ref.upper()):
            flash("Jira format must follow MOTOR-.", "danger")
            return redirect(url_for("routes.tickets"))

        # Prevent duplicate Jira references
        existing = Ticket.query.filter(
            Ticket.external_ref == external_ref.upper(),
            Ticket.status != "deleted",
        ).first()

        if existing:
            flash(
                "This Jira reference is already in the buddy workflow.",
                "danger",
            )
            return redirect(url_for("routes.tickets"))

        external_ref = external_ref.upper()

        # create a new ticket to the board
        # status defaults to "ready_for_buddy" in the model
        ticket = Ticket(
            external_ref=external_ref,
            title=title,
            created_by_id=current_user.id,
        )
        db.session.add(ticket)
        db.session.commit()

        flash("Ticket added to the buddy queue.", "success")
        return redirect(url_for("routes.tickets"))

    # show tickets in three groups for the buddy board.
    # newest tickets first so the queue makes sense to testers
    all_tickets = Ticket.query.order_by(Ticket.created_at.asc()).all()

    tickets_by_status = {
        "ready_for_buddy": [
            t for t in all_tickets if t.status == "ready_for_buddy"
        ],
        "buddied": [
            t for t in all_tickets if t.status == "buddied"
        ],
        "deleted": [
            t for t in all_tickets if t.status == "deleted"
        ],
    }

    return render_template(
        "tickets.html",
        tickets_by_status=tickets_by_status,
    )


# move a ticket from ready_for_buddy to buddied.
@bp.route("/tickets/<int:ticket_id>/buddied", methods=["POST"])
@login_required
def mark_ticket_buddied(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)

    # only tickets actually waiting for buddy can be moved
    if ticket.status != "ready_for_buddy":
        flash("This ticket is not ready to be buddied.", "warning")
        return redirect(url_for("routes.tickets"))

    # guest users stay read-only
    if current_user.is_guest:
        flash("Guest users cannot update tickets.", "warning")
        return redirect(url_for("routes.tickets"))

    # prevent users from buddying their own tickets
    if ticket.created_by_id == current_user.id:
        flash("You cannot buddy a ticket that you created.", "warning")
        return redirect(url_for("routes.tickets"))

    ticket.status = "buddied"
    ticket.buddy_id = current_user.id
    ticket.ready_at = datetime.utcnow()

    db.session.commit()
    flash("Ticket marked as buddied.", "success")
    return redirect(url_for("routes.tickets"))


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

    # passing for table and dropdown
    users = User.query.all()
    roles = Role.query.all()
    return render_template("admin.html", users=users, roles=roles)


# update a users role if admin
@bp.route("/admin/update-role", methods=["POST"])
@login_required
def admin_update_role():
    if not current_user.is_admin:
        flash(
            "You do not have permission to view that page.",
            "danger",
        )
        return redirect(url_for("routes.index"))

    user_id = request.form.get("user_id", type=int)
    role_id = request.form.get("role_id", type=int)

    # validate inputs exist
    if not user_id or not role_id:
        flash("Invalid form submission.", "danger")
        return redirect(url_for("routes.admin"))

    user = User.query.get(user_id)
    role = Role.query.get(role_id)
    if not user or not role:
        flash("Invalid user or role.", "danger")
        return redirect(url_for("routes.admin"))

    # if user is already in this role, do nothing
    existing_link = UserRole.query.filter_by(
        user_id=user.id,
        role_id=role.id,
    ).first()
    if existing_link:
        flash(
            f"No change: {user.username} already has this role.",
            "info",
        )
        return redirect(url_for("routes.admin"))

    # replace any existing, with the new one
    UserRole.query.filter_by(user_id=user.id).delete(synchronize_session=False)
    db.session.add(UserRole(user_id=user.id, role_id=role.id))
    db.session.commit()

    flash(f"Updated {user.username} to role {role.name}.", "success")
    return redirect(url_for("routes.admin"))


# deactivate user logic
@bp.route("/admin/delete-user", methods=["POST"])
@login_required
def admin_delete_user():

    if not current_user.is_admin:
        flash("You do not have permission to do that.", "danger")
        return redirect(url_for("routes.index"))

    user_id = request.form.get("user_id", type=int)
    if user_id == current_user.id:
        flash("You cannot deactivate your own account.", "warning")
        return redirect(url_for("routes.admin"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("routes.admin"))

    # deactive user rather than delete
    user.is_active = False
    db.session.commit()

    flash(f"User {user.username} has been deactivated.", "success")
    return redirect(url_for("routes.admin"))


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

        # block login if deactivated
        if user and not user.is_active:
            flash(
                "Your account has been deactivated. Please contact Admin.",
                "danger",
            )
            return redirect(url_for("routes.login"))

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

        # check to stop blank spaces as a password
        if not password.strip() or not confirm_password.strip():
            flash("Password cannot be empty or spaces only.", "danger")
            return redirect(url_for("auth.register"))

        # minimum length for the password
        if len(password.strip()) < MIN_PASSWORD_LENGTH:
            msg = (
                f"Password must be at least "
                f"{MIN_PASSWORD_LENGTH} characters long."
            )
            flash(msg, "danger")
            return redirect(url_for("routes.register"))

        # password must contain at least one letter and one number
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)

        if not (has_letter and has_number):
            flash(
                "Password must contain at least one letter and one number.",
                "danger"
            )
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
