from .base import *

DEBUG = True

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

INSTALLED_APPS += ["debug_toolbar"]
ROOT_URLCONF = "config.urls_dev"
MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
