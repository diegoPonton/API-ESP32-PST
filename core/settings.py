# core/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

# --- Paths base ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad / Entorno ---
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "telemetry",
]

# --- Middleware ---
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# --- URL / WSGI ---
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# --- Templates (requisito del admin) ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --- Base de datos (sqlite para dev; en Railway puedes usar Postgres) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Internacionalización ---
LANGUAGE_CODE = "es-es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # útil para Railway (collectstatic)

# --- DRF / CORS ---
CORS_ALLOW_ALL_ORIGINS = True  # en prod usa lista blanca
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (),  # luego activamos JWT si quieres
}

# --- InfluxDB (vars de entorno) ---
INFLUX_URL    = os.getenv("INFLUX_URL", "")
INFLUX_TOKEN  = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG    = os.getenv("INFLUX_ORG", "")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "iot")

# --- Django 4: id por defecto ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
