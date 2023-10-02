import os

from .base import *  # noqa: F401, F403

DEBUG = False

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

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "'smtp.mailgun.org'"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_USE_TLS = True
