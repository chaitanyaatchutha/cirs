# Campus Complaint Management System — Deployment Guide

This package is prepared for public deployment as a Flask application.

## Important security step

The original project contained a Gmail App Password in `app.py`. That secret has been removed from this deployment package. **Revoke the old Gmail App Password before publishing the project to GitHub.** Create a new App Password and put it in the hosting provider's environment variables.

The original hard-coded admin passwords have also been removed. Initial admin accounts are supplied through `ADMIN_DEFAULTS_JSON`.

## 1. Create a cloud MySQL database

Use any managed MySQL provider that gives you a host, port, username, password and database name. Create a database named `cirs` (or set another name in `MYSQL_DATABASE`).

The app creates its three tables automatically when it can connect:
- students
- admins
- complaints

Some managed MySQL services do not allow `CREATE DATABASE`. In that case, create the database in the provider dashboard and keep `MYSQL_DATABASE` set to that database name.

## 2. Push this folder to GitHub

Do NOT commit `.env` files or real credentials.

Recommended GitHub files include:
- `app.py`
- `model.pkl`
- `vectorizer.pkl`
- `requirements.txt`
- `Procfile`
- `render.yaml`
- `templates/`
- `README_DEPLOY.md`

## 3. Deploy to Render

Create a Render Web Service from the GitHub repository.

Build command:

    pip install -r requirements.txt

Start command:

    gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120

The included `render.yaml` can be used as a starting point for these settings.

## 4. Add environment variables

Set these in Render:

- `FLASK_SECRET_KEY`
- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`
- `SMTP_EMAIL`
- `SMTP_APP_PASSWORD`
- `EMAIL_ELECTRICAL`
- `EMAIL_MAINTENANCE`
- `EMAIL_CSE`
- `EMAIL_ECE`
- `EMAIL_CLEANING`
- `EMAIL_HOSTEL`
- `EMAIL_OTHERS`
- `EMAIL_LIBRARY`
- `ADMIN_DEFAULTS_JSON`

Example admin JSON:

    [["electrical","use-a-strong-password","Electrical"],["maintenance","use-a-strong-password","Maintenance"]]

Use a different strong password for every administrator. After first login, admins can use the existing change-password page.

## 5. Test after deployment

Open:

    /health

Expected response:

    {"status":"ok"}

Then test:
1. Student registration
2. Student login
3. Complaint submission
4. ML department prediction
5. Complaint status
6. Department admin login
7. Status update
8. Department email notification

## Local development

Copy `.env.example` to `.env` and fill it with your local values. This project does not automatically load `.env`; for local use, either set the variables in your shell or install `python-dotenv` and load it before importing the app.

Run:

    python app.py

or:

    gunicorn app:app --bind 0.0.0.0:5000 --workers 1 --timeout 120
