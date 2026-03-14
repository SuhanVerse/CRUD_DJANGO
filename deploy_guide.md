# Deploying Grocery Bud to Render - Full Guide

This guide covers everything from preparing your code to getting your live URL on Render using only SQLite.

---

## Files for Deployment

```
CRUD_DJANGO/
|- Procfile              <- Start command reference for Gunicorn
|- runtime.txt           <- Pins Python version (optional on Render)
|- requirements.txt      <- Python dependencies
|- .env.example          <- Template for local environment variables
|- .gitignore            <- Keeps git clean
`- config/
    `- settings.py        <- Production-ready env vars, WhiteNoise, SQLite
```

---

## STEP 1 - Pre-Push Checklist

Before pushing to GitHub, confirm the repository root contains:

- `manage.py`
- `requirements.txt`
- `Procfile`
- `runtime.txt`

Confirm these are **not** committed:

- `.env`
- `db.sqlite3`

Run local validation commands:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py collectstatic --noinput
```

---

## STEP 2 - Generate a Secret Key and Create `.env`

Generate a key locally:

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Create your local `.env` file:

```bash
cp .env.example .env
```

Example local `.env` values:

```env
SECRET_KEY=<your-generated-key>
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

Notes:

- `python-decouple` reads `.env` locally.
- In Render, use dashboard environment variables instead of a checked-in `.env`.
- Never commit `.env`.
- Use a different `SECRET_KEY` in production.

---

## STEP 3 - Push to GitHub

If the repository is not connected yet:

```bash
git init
git branch -M main
git add .
git commit -m "Prepare Render deployment"
git remote add origin https://github.com/<your-username>/<your-repository>.git
git push -u origin main
```

If the repository already exists:

```bash
git add .
git commit -m "Switch deployment to Render"
git push origin main
```

---

## STEP 4 - Create the Render Web Service

1. Open [Render](https://render.com) and sign in.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub account (if needed).
4. Select this repository.
5. Set these values:
    - **Environment**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
    - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file -`
6. Click **Create Web Service**.

---

## STEP 5 - Do Not Create Any Render Database Service

1. Do **not** create PostgreSQL on Render for this project.
2. This app is configured to use `db.sqlite3` only.
3. Skip all Render database setup screens.

---

## STEP 6 - Configure Render Environment Variables

In your Render web service, add:

```env
SECRET_KEY=<paste-a-new-random-secret>
DEBUG=false
ALLOWED_HOSTS=<your-service>.onrender.com,.onrender.com
CSRF_TRUSTED_ORIGINS=https://<your-service>.onrender.com
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
```

Important notes:

- `SECRET_KEY` is required.
- `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` must match your final Render domain.
- No `DATABASE_URL` is required for this setup.
- SQLite on Render is file-based; data may reset on redeploy/restart unless you attach a persistent disk.

---

## STEP 7 - First Deployment Log Check

After first deploy, confirm in logs:

- Dependencies installed successfully.
- `collectstatic` completed successfully.
- Gunicorn started without import errors.
- No missing variable errors for `SECRET_KEY`.
- No WhiteNoise manifest startup errors.

---

## STEP 8 - Run Migrations on Render

After the app is deployed:

1. Open your Render web service.
2. Open **Shell**.
3. Run:

```bash
python manage.py migrate
```

---

## STEP 9 - Create a Superuser

In Render shell:

```bash
python manage.py createsuperuser
```

Then log in at:

`https://<your-service>.onrender.com/admin`

---

## STEP 10 - Post-Deploy Verification Checklist

Verify all of the following in production:

1. Home page loads on your Render domain.
2. Add item works.
3. Edit item works.
4. Delete item works.
5. Toast messages appear.
6. Static assets load correctly.
7. Admin panel is accessible.

---

## STEP 11 - Auto Deploys

Render redeploys when you push to the tracked branch (usually `main`):

```bash
git add .
git commit -m "Update something"
git push
```

---

## Troubleshooting

**App crashes on startup**
- Check `SECRET_KEY` is set in Render environment variables.
- Check `ALLOWED_HOSTS` includes your Render hostname.

**CSRF failures on forms**
- Ensure `CSRF_TRUSTED_ORIGINS` contains full `https://...` origin.
- Ensure domain matches your current Render URL.

**Static files return 404**
- Confirm `whitenoise` is installed.
- Confirm `collectstatic` succeeded during build.
- Check for manifest errors at startup.

**`DisallowedHost` error**
- Ensure `ALLOWED_HOSTS` includes `.onrender.com`.

**500 on first load**
- Run migrations in Render shell: `python manage.py migrate`.

**Data disappears after restart/redeploy**
- Expected with ephemeral filesystem when using plain SQLite.
- If you need persistence without PostgreSQL, attach a Render persistent disk and store `db.sqlite3` on that disk path.
