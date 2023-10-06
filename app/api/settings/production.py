import os

from .base import *  # noqa: F401, F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE"),
        "NAME": os.environ.get("DB_DATABASE"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": int(os.environ.get("DB_PORT")),  # type: ignore[arg-type]
    }
}

_PORT = os.environ.get("NGINX_PORT", "")
if not _PORT.isdigit():
    raise ValueError("NGINX_PORT must be a digit")
CSRF_TRUSTED_ORIGINS = [f"http://localhost:{_PORT}"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("REDIS_BACKEND"),
    },
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
