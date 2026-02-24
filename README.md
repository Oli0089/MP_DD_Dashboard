# Comparison App (MP)


## Overview


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
- Tester / Developer / BA
- Guest – readonly

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

## Testing Strategy
To be ran within the virtual envrioment

**BDD Tests (Behave)**
- behave
**Unit Tests (pytest)**
- pytest
**Linting**
- flake8

All tests also run automatically via GitHub Actions
