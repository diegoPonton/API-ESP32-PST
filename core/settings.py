# core/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# ---------------------------
# Helpers
# ---------------------------
def _get_bool(env_name: str, default: bool = False) -> bool:
    return os.getenv(env_name, str(default)).strip().lower() in ("1", "true", "yes", "on")

def _get_list(env_name: str, default: str = ""):
    raw = os.getenv(env_name, default)
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]

# ---------------------------
# Paths
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------
# Seguridad / Entorno
# ---------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev")
DEBUG = _get_bool("DEBUG", False)

# Hosts permitidos (coma-separados). En Railway puedes dejar "*"
ALLOWED_HOSTS = _get_list("ALLOWED_HOSTS", "*")

# CSRF (necesario cuando sirves HTTPS detrás de proxy, p.ej. Railway).
# Usa URLs completas con esquema, por ejemplo: https://tu-app.up.railway.app
CSRF_TRUSTED_ORIGINS = _get_list("CSRF_TRUSTED_ORIGINS", "")

# Token Bearer para escritura desde el ESP32
API_WRITE_TOKEN = os.getenv("API_WRITE_TOKEN", "")

# ---------------------------
# Apps
# ---------------------------
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

# ---------------------------
# Middleware
# ---------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise: servir estáticos en producción
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------
# URL / WSGI
# ---------------------------
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

# ---------------------------
# Templates (requisito del admin)
# ---------------------------
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

# ---------------------------
# Base de datos
# (sqlite para dev; si luego quieres Postgres en Railway, lo cambiamos)
# ---------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ---------------------------
# Internacionalización
# ---------------------------
LANGUAGE_CODE = "es-es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------
# Archivos estáticos
# ---------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise: empaquetado comprimido en producción
if not DEBUG:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------
# DRF / CORS
# ---------------------------
# CORS: por defecto todo permitido en dev; en prod usa lista blanca
CORS_ALLOW_ALL_ORIGINS = _get_bool("CORS_ALLOW_ALL_ORIGINS", True)
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = _get_list("CORS_ALLOWED_ORIGINS", "")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (),  # si luego quieres JWT lo activamos
}

# ---------------------------
# InfluxDB (Cloud)
# ---------------------------
INFLUX_URL    = os.getenv("INFLUX_URL", "")
INFLUX_TOKEN  = os.getenv("INFLUX_TOKEN", "")
INFLUX_ORG    = os.getenv("INFLUX_ORG", "")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "iot")

# ---------------------------
# Django 4: id por defecto
# ---------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
