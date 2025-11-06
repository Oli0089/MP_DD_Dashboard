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
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    # links to roles table
    roles = db.relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # tickets created by this user
    tickets_created = db.relationship(
        "Ticket",
        foreign_keys="Ticket.created_by_id",
        back_populates="creator",
    )

    # tickets where this user is the buddy
    tickets_buddy = db.relationship(
        "Ticket",
        foreign_keys="Ticket.buddy_id",
        back_populates="buddy",
    )

    # returns admin for user if so
    @property
    def is_admin(self):
        return any(link.role and link.role.name == "Admin" for link in self.roles)


# links users and roles tables
class UserRole(db.Model):
    __tablename__ = "user_roles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)

    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")


class Ticket(db.Model):
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)

    # link to internal tickets
    external_ref = db.Column(db.String(50), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(db.DateTime, default=datetime.now(datetime.timezone.utc))
    ready_at = db.Column(db.DateTime, nullable=True)

    # who raised the ticket
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # who is the buddy on this ticket
    buddy_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    creator = db.relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="tickets_created",
    )
    buddy = db.relationship(
        "User",
        foreign_keys=[buddy_id],
        back_populates="tickets_buddy",
    )
