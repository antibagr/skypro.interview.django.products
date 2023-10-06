from .base import *  # noqa: F401, F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
        "OPTIONS": {"timeout": 25},
    }
}


# EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# EMAIL_FILE_PATH = BASE_DIR / "tmp" / "emails"
