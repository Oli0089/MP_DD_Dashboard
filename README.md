# Buddy Ticket Tracker (Lvl6 SEDO Project)
A secure Flask-based ticket board for “Buddy” reviews, built for the Level 6 Software Engineering & DevOps module

## Overview
The Buddy Ticket Tracker is a lightweight internal tool designed to support the QA “buddy” review workflow.
It displays tickets awaiting review, highlights their age, supports login with rolebased permissions and provides an admin panel for managing users.

**This application supports DevOps best practice through:**
Automated CI via GitHub Actions
Secure configuration via environment variables
Deployment on Render with a PostgreSQL database
Automated database initialisation with role seeding
BDD testing using Behave
RBAC and session security (CSRF, hashed passwords, etc)

## Key Features
**User Authentication**
- Registration, login, logout
- Password hashing and session protection with CSRF tokens
- Separate admin and non-admin views

**Role-Based Access Control**
Roles stored in the DB:

- Admin – full access: manage users/roles, view everything
- Tester / Developer / BA – create + manage tickets
- Guest – readonly

**Ticket Managment**
- Create tickets ready for “buddy” review
- Buddy other users Tickets
- View all tickets
- Ticket ageing colour logic:
    - Green < 1 day
    - Amber 1–3 days
    - Red > 3 days
- Audit timestamps

**Admin Panel**
- List all users
- View accepable user details
- Update user roles
- Deactive Users

**Security**
- CSRF protection (Flask-WTF)
- App secrets stored in environment variables
- Postgres credentials stored securely in Render
- Hashed passwords
- Login protected routes
- Input validation on forms
- RBAC enforced
- Secure cookies sessions


## Data Model
Tables:
- users
- roles
- user_roles (many-to-many relationship)
- tickets

Base roles (Admin, Tester, Developer, BA, Guest)

## DevOps & CI/CD
**GitHub Actions**
The repository includes a workflow that runs on every push:
- flake8 linting
- pytest (unit tests)
- behave (BDD tests)
- failures block merge to main

**Deployment**
Deployment is handled on Render:
- Render automatically deploys when changes are pushed to main
- The app connects to a managed PostgreSQL instance

## Production Deployment (Render)
**Live URL:**
 - https://softwaredevops-buddytracker.onrender.com

**Test Admin Account**
Role = Admin
- Username:...
- Password:...

**Test Role Based Account**
Role = Tester
- Username:...
- Password:...

**Test Guest Account**
Role = Guest
- Username:...
- Password:...

## Local Development Setup
**Requirments**
Python 3.11+
Git
Virtual environment support (Visual Studio Code)

**Clone the Repo**
git clone https://github.com/Oli0089/SoftwareDevOps_BuddyTracker.git
cd SoftwareDevOps_BuddyTracker

**Create/activate the virtual environment**
Windows
 - python -m venv .venv
 - .\.venv\Scripts\activate.bat
MacOS/Linux:
- python3 -m venv .venv
- source .venv/bin/activate

**Install Dependencies**
pip install -r requirements.txt

**Environment Variables**
Create a .env file in the root folder with
 - SECRET_KEY=dev-secret-key
 - FLASK_ENV=development

**Run the application**
flask run

App runs at:
- http://127.0.0.1:5000

## Testing Strategy
To be ran within the virtual envrioment
**BDD Tests (Behave)**
behave
**Unit Tests (pytest)**
pytest
**Linting**
flake8

All tests also run automatically via GitHub Actions

## Useful Links
Live App: https://softwaredevops-buddytracker.onrender.com
Repository: https://github.com/Oli0089/SoftwareDevOps_BuddyTracker
