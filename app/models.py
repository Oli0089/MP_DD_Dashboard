# app/models.py
from datetime import datetime
from . import db
# Database basics used from Lvl 5 Module


class Role(db.Model):

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # many-to-many table
    users = db.relationship("UserRole", back_populates="role")


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # stores a hashed password
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    last_login = db.Column(db.DateTime, nullable=True)

    # Flag to soft-deactivate accounts instead of hard deleting
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # links to roles table
    roles = db.relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # returns admin for user if so
    @property
    def is_admin(self):
        return any(
            link.role and link.role.name == "Admin"
            for link in self.roles
        )

    # return guest users for read only access
    @property
    def is_guest(self):
        # true if user has Guest and is not an Admin
        return (
            any(
                link.role and link.role.name == "Guest"
                for link in self.roles
            )
            and not self.is_admin
        )

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self):
        return True


# links users and roles tables
class UserRole(db.Model):
    __tablename__ = "user_roles"

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"), primary_key=True
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"), primary_key=True
    )

    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")


# Stores one full DD run (one press of "Finalise DD Run")
class DDRun(db.Model):
    __tablename__ = "dd_runs"

    id = db.Column(db.Integer, primary_key=True)

    # Latest DD version
    dd_version = db.Column(db.String(20), nullable=False)

    # Previous DD for comparison
    compared_against = db.Column(db.String(20), nullable=False)

    # Overall (Passed / Failed)
    status = db.Column(db.String(20), nullable=False)

    # When the run was finalised
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Who ran the DD - actual value
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Allows Results page for full User object
    user = db.relationship("User")

    # Relationship to all SWH results under this run
    results = db.relationship(
        "SWHResult",
        back_populates="dd_run",
        cascade="all, delete-orphan"
    )


# Stores the result of each SWH transaction within a DD run
class SWHResult(db.Model):
    __tablename__ = "swh_results"

    id = db.Column(db.Integer, primary_key=True)

    # Key used in config (e.g. "cdl_nb_comp")
    swh_key = db.Column(db.String(80), nullable=False)

    # Display name (e.g. "CDL NB Comp")
    swh_name = db.Column(db.String(120), nullable=False)

    # Result of this SWH (Passed / Failed)
    status = db.Column(db.String(20), nullable=False)

    # Comma-separated failed variants (e.g. "CX" or "CA,CV")
    failed_variants = db.Column(db.String(120), nullable=True)

    # Link back to the DD run this belongs to
    dd_run_id = db.Column(
        db.Integer,
        db.ForeignKey("dd_runs.id"),
        nullable=False
    )

    # Relationship back to DDRun
    dd_run = db.relationship("DDRun", back_populates="results")
