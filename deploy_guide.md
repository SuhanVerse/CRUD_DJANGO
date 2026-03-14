# Deploying Grocery Bud to Railway — Full Guide

This guide covers everything from preparing your code to getting your live URL on Railway.

---

## Files for Deployment

```
CRUD_DJANGO/
├── Procfile              <- Railway runs this to start the app
├── runtime.txt           <- Pins the Python version
├── requirements.txt      <- Python dependencies
├── .env.example          <- Template for local environment variables
├── .gitignore            <- Keeps git clean
└── config/
    └── settings.py       <- Updated for production (env vars, WhiteNoise, PostgreSQL)
```

---

## STEP 1 — Pre-Push Checklist

Before pushing to GitHub, confirm the repository root contains:

- `manage.py`
- `requirements.txt`
- `Procfile`
- `runtime.txt`

Confirm these are **not** committed:

- `.env`
- `db.sqlite3`

Run the final local validation commands:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py collectstatic --noinput
```

---

## STEP 2 — Generate a Secret Key and Create `.env`

### Generate your secret key

Run one of these in your terminal:

**Option A — Using Django (recommended):**

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Option B — Using Python only:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Create your `.env` file

Copy the example and fill in your key:

```bash
cp .env.example .env
```

Then edit `.env` and paste your generated key into `SECRET_KEY=`.

Your `.env` for local development should look like:

```env
SECRET_KEY=<your-generated-key>
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

> `python-decouple` reads this `.env` file automatically when running locally.
> When deployed to Railway, it uses environment variables from the dashboard instead.
> **Never commit `.env` to GitHub** — your `.gitignore` already excludes it.
> Use a **different key** for local vs. production.

---

## STEP 3 — Push to GitHub

If the repository is not connected yet:

```bash
git init
git branch -M main
git add .
git commit -m "Prepare Railway deployment"
git remote add origin https://github.com/<your-username>/<your-repository>.git
git push -u origin main
```

If the repository already exists:

```bash
git add .
git commit -m "Switch deployment from Render to Railway"
git push origin main
```

---

## STEP 4 — Create the Railway Project

1. Open [Railway](https://railway.com).
2. Click **New Project**.
3. Choose **Deploy from GitHub repo**.
4. Select this repository.
5. Railway will create a web service for the Django app.

---

## STEP 5 — Provision PostgreSQL

1. In the same Railway project, click **New** and add a **PostgreSQL** service.
2. Wait until Railway provisions the database.
3. Open the PostgreSQL service and confirm that `DATABASE_URL` is available.

---

## STEP 6 — Configure Railway Environment Variables

Open the Django web service and add these variables:

```env
SECRET_KEY=<paste-a-new-random-secret>
DEBUG=false
ALLOWED_HOSTS=<your-service>.up.railway.app,.railway.app
CSRF_TRUSTED_ORIGINS=https://<your-service>.up.railway.app
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_CONN_MAX_AGE=600
DB_SSL_REQUIRE=True
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=True
DJANGO_SECURE_HSTS_PRELOAD=True
```

Important notes:

- `DATABASE_URL` is required — the app will fall back to SQLite if missing, which is wrong for production.
- `SECRET_KEY` is required — the app will crash on startup without it.
- `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` should match the final Railway public domain.
- Use `${{Postgres.DATABASE_URL}}` to reference the Railway PostgreSQL service variable.

---

## STEP 7 — What Railway Will Run Automatically

Railway uses these root files during deployment.

### requirements.txt

Railway detects this file and runs `pip install -r requirements.txt` automatically.

### Procfile

```procfile
web: python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --log-file -
```

This collects static files and starts Gunicorn on every deploy.

### runtime.txt

```txt
python-3.12.3
```

---

## STEP 8 — First Deployment Log Check

After the first deploy, inspect the deployment logs and confirm:

- Dependencies installed successfully.
- `collectstatic` completed successfully.
- Gunicorn started without import errors.
- There is no `UndefinedValueError` for `SECRET_KEY` or `DATABASE_URL`.
- There is no static manifest error from WhiteNoise startup.

---

## STEP 9 — Run Migrations

After the application deploys successfully, run the database setup inside the Railway web service environment.

### Option A: Railway Dashboard Shell

1. Open the web service.
2. Open the latest deployment.
3. Open the service shell.
4. Run:

```bash
python manage.py migrate
```

### Option B: Railway CLI

Install Railway CLI, log in, then run:

```bash
railway login
railway link
railway shell
python manage.py migrate
exit
```

---

## STEP 10 — Create a Superuser (Admin Access)

In the Railway shell, create an admin account:

```bash
python manage.py createsuperuser
```

Enter a username, email, and password. Then visit `https://<your-service>.up.railway.app/admin` to log in.

---

## STEP 11 — Post-Deploy Verification Checklist

Verify all of the following in production:

1. The home page loads on the Railway public domain.
2. You can add a grocery item.
3. You can edit a grocery item.
4. You can delete a grocery item.
5. Toast messages appear correctly.
6. Static assets (CSS, favicon) load correctly.
7. Admin panel is accessible and functional.

---

## STEP 12 — Auto-Deploys

Railway automatically redeploys your app every time you push to `main`:

```bash
git add .
git commit -m "Update something"
git push
```

Railway picks it up and deploys within minutes.

---

## Troubleshooting

**App crashes on boot**
- Check that `SECRET_KEY` is set in Railway environment variables.
- Check that `DATABASE_URL` is mapped from the PostgreSQL service.
- Check that `ALLOWED_HOSTS` matches the Railway hostname.

**CSRF failure on forms**
- Check that `CSRF_TRUSTED_ORIGINS` contains the full `https://...` origin.
- Make sure you are using the final Railway public URL, not an old preview URL.

**Static files return 404**
- Check that `whitenoise` is installed.
- Check that `collectstatic` succeeded in the deployment logs.
- Check there is no manifest generation error during startup.

**`DisallowedHost` error**
- Make sure `ALLOWED_HOSTS` env var includes `.railway.app` (note the leading dot).

**500 error on first load**
- Check if migrations ran. In the Railway shell: `python manage.py migrate`

**Database connection error**
- Make sure `DATABASE_URL` is set and references the Railway PostgreSQL service.
- If using `DB_SSL_REQUIRE=True`, ensure the database supports SSL connections.
