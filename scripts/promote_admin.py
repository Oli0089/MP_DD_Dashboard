import os
import sys
from app import create_app, db
from app.models import User, Role, UserRole
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)


# Change to username wanting to be admin
USERNAME = "OliverKeeys"


# Used for testing to update a user as admin
def main():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=USERNAME).first()
        if user is None:
            print(f"User '{USERNAME}' not found")
            return

        admin_role = Role.query.filter_by(name="Admin").first()

        link = UserRole.query.filter_by(
            user_id=user.id,
            role_id=admin_role.id
        ).first()
        if link is None:
            db.session.add(UserRole(user_id=user.id, role_id=admin_role.id))

        db.session.commit()
        print(f"User '{USERNAME}' promoted to Admin and set active.")


if __name__ == "__main__":
    main()
