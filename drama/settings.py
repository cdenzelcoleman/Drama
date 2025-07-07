# drama/settings.py

import os
from pathlib import Path
import environ

# ─── ENV VARS ───────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
)
# load .env file if present
env_file = BASE_DIR / ".env"
if env_file.exists():
    env.read_env(str(env_file))

# required
SECRET_KEY = env("SECRET_KEY", default="django-insecure-change-me-in-production")
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=['localhost', '127.0.0.1', '0.0.0.0', '192.168.1.69'])
# Add testserver for Django testing
if 'testserver' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('testserver')

# ─── INSTALLED APPS ─────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",



    # your apps
    "accounts.apps.AccountsConfig",
    "movies.apps.MoviesConfig",
    "games.apps.GamesConfig",
]


TMDB_API_KEY = env("TMDB_API_KEY", default="")


# ─── MIDDLEWARE ─────────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "drama.urls"

# ─── TEMPLATES ──────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "drama.wsgi.application"
ASGI_APPLICATION = "drama.asgi.application"

# Channels
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# ─── DATABASE ───────────────────────────────────────────────────────
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}
# ─── AUTHENTICATION ─────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
)
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Session configuration
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# ─── VALIDATORS ──────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ─── INTERNATIONALIZATION ─────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ─── STATIC FILES ────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─── MEDIA FILES ─────────────────────────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
