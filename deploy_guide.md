# 🚀 Deploying Grocery Bud to Render — Full Guide

This guide covers everything from preparing your code to getting your live URL.

---

## 📁 Files Added for Deployment

```
CRUD_DJANGO/
├── build.sh              ← Render runs this on every deploy
├── render.yaml           ← Defines your services (Blueprint method)
├── requirements.txt      ← Python dependencies
├── .gitignore            ← Keeps git clean
└── config/
    └── settings.py       ← Updated for production (env vars, WhiteNoise, PostgreSQL)
```

---

## STEP 1 — Install New Dependencies Locally

```bash
pip install gunicorn whitenoise psycopg2-binary dj-database-url python-decouple

# Freeze to requirements.txt
pip freeze > requirements.txt
```

Your `requirements.txt` should contain at minimum:
```
django>=4.2,<5.0
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
python-decouple==3.8
```

---

## STEP 2 — Create a `.env` File for Local Development

Create `.env` in your project root (never commit this file):

```env
SECRET_KEY=your-local-dev-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
```

> ✅ `python-decouple` reads this file automatically.  
> ✅ When deployed, Render sets these as environment variables instead.

---

## STEP 3 — Updated `config/settings.py`

The settings file now uses **environment variables** for everything sensitive:

```python
from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'grocery',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← Must be 2nd
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'config.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL = config('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL)
}

# ─── Static Files ─────────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

---

## STEP 4 — Create `build.sh`

This script runs automatically on every Render deploy:

```bash
#!/usr/bin/env bash
set -o errexit       # Exit immediately if any command fails

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate
```

Make it executable:

```bash
chmod +x build.sh
```

---

## STEP 5 — Create `render.yaml` (Blueprint)

This file lets Render auto-configure both your web service and database:

```yaml
databases:
  - name: grocery-db
    databaseName: grocery_bud
    user: grocery_user
    plan: free

services:
  - type: web
    name: grocery-bud
    env: python
    plan: free
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: grocery-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: ALLOWED_HOSTS
        value: ".onrender.com"
      - key: PYTHON_VERSION
        value: "3.11.0"
```

---

## STEP 6 — Push to GitHub

```bash
# Initialize git (if not done already)
git init
git add .
git commit -m "Initial commit — ready for Render deployment"

# Create a repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

> ⚠️ Make sure `.gitignore` excludes `venv/`, `.env`, and `db.sqlite3`

---

## STEP 7 — Deploy on Render

### Option A — Blueprint (Recommended, Automatic)

1. Go to [https://render.com](https://render.com) and log in
2. Click **New +** → **Blueprint**
3. Connect your GitHub account and select your repository
4. Render will detect `render.yaml` and create both the **database** and **web service** automatically
5. Click **Apply**
6. Wait ~3–5 minutes for the build to finish
7. Click the generated `.onrender.com` URL — your app is live! 🎉

---

### Option B — Manual (Dashboard)

**First, create the PostgreSQL database:**

1. Click **New +** → **PostgreSQL**
2. Name: `grocery-db`, Region: `Oregon` (or nearest), Plan: `Free`
3. Click **Create Database**
4. Wait until status shows **Available**
5. Copy the **Internal Database URL** from the Connections section

**Then, create the web service:**

1. Click **New +** → **Web Service**
2. Connect your GitHub repo
3. Fill in the settings:

| Field | Value |
|-------|-------|
| Name | `grocery-bud` |
| Runtime | `Python 3` |
| Build Command | `./build.sh` |
| Start Command | `gunicorn config.wsgi:application` |
| Plan | `Free` |

4. In the **Environment Variables** section, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Click "Generate" for a random value |
| `DEBUG` | `false` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | Paste the Internal Database URL from step 5 above |
| `PYTHON_VERSION` | `3.11.0` |

5. Click **Create Web Service**
6. Watch the build logs — it should end with `==> Your service is live 🎉`

---

## STEP 8 — Create a Superuser (Admin Access)

After deployment, use the Render Shell to create an admin account:

1. In your web service dashboard, click **Shell**
2. Run:

```bash
python manage.py createsuperuser
```

3. Enter a username, email, and password
4. Visit `https://YOUR-APP.onrender.com/admin` to log in

---

## 🔄 Auto-Deploys

Render automatically redeploys your app every time you push to `main`:

```bash
git add .
git commit -m "Update something"
git push
```

That's it — Render picks it up and deploys within minutes.

---

## ⚠️ Free Tier Limitations

| Limitation | Details |
|-----------|---------|
| Sleep after inactivity | Web service sleeps after 15 min of no traffic (cold start ~30s) |
| PostgreSQL expiry | Free databases are deleted after **90 days** |
| Storage | 1 GB for the free PostgreSQL database |
| Bandwidth | 100 GB/month |

To avoid sleep, consider upgrading to the Starter plan ($7/month) or use a service like UptimeRobot to ping your app every 14 minutes.

---

## 🐛 Troubleshooting

**Build fails with `ModuleNotFoundError`**  
→ Check that `requirements.txt` includes all packages. Run `pip freeze > requirements.txt` locally and push again.

**`DisallowedHost` error**  
→ Make sure `ALLOWED_HOSTS` env var is set to `.onrender.com` (note the leading dot).

**Static files (CSS) not loading**  
→ Ensure `whitenoise.middleware.WhiteNoiseMiddleware` is in `MIDDLEWARE` as the **2nd entry**, and `STATIC_ROOT` is set. The `build.sh` must run `collectstatic`.

**500 error on first load**  
→ Check if migrations ran. In the Render Shell: `python manage.py migrate`

**Database connection error**  
→ Make sure `DATABASE_URL` is set to the **Internal** URL (not external) in your Render environment variables.
