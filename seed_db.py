# seed_db.py
# helper script to create tables for local dev db

from app import create_app, db
from app.models import Role


# create tables and insert base roles if they do not exist
def main():
    app = create_app()

    with app.app_context():
        db.create_all()  # creates tables in SQLite

        base_roles = ["Admin", "Tester", "Developer", "BA", "Guest"]

        for name in base_roles:
            # only add the role if it is not already there
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name))

        db.session.commit()
        print("Database created and base roles seeded.")


if __name__ == "__main__":
    main()
