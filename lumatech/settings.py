"""Django settings for the Luma Tech Solutions website."""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-key-change-me-please-do-not-use-in-production-xyz123",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        "DJANGO_ALLOWED_HOSTS",
        "localhost,127.0.0.1,lumatechsolutions.co.uk,www.lumatechsolutions.co.uk",
    ).split(",")
    if h.strip()
]

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "https://lumatechsolutions.co.uk,https://www.lumatechsolutions.co.uk",
    ).split(",")
    if o.strip()
]

# Caddy terminates TLS in front of us; trust the X-Forwarded-Proto header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.admin",
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lumatech.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site",
            ],
        },
    },
]

WSGI_APPLICATION = "lumatech.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(os.environ.get("DJANGO_DB_PATH", BASE_DIR / "data" / "db.sqlite3")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Email ---
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", "0") == "1"
# TLS and SSL are mutually exclusive in Django; SSL wins if both are set.
EMAIL_USE_TLS = (not EMAIL_USE_SSL) and os.environ.get("DJANGO_EMAIL_USE_TLS", "1") == "1"
DEFAULT_FROM_EMAIL = os.environ.get(
    "DJANGO_DEFAULT_FROM_EMAIL", "Luma Tech Solutions <hello@lumatechsolutions.co.uk>"
)
CONTACT_FORM_RECIPIENT = os.environ.get(
    "CONTACT_FORM_RECIPIENT", "hello@lumatechsolutions.co.uk"
)

# --- reCAPTCHA v3 (contact form) ---
# Site key is public and ships in HTML — fine to commit. Secret key is
# server-side only and MUST be set via env var in production. When the secret
# is empty (e.g. local dev), verification is skipped and the form behaves as
# if reCAPTCHA wasn't there. Submissions below RECAPTCHA_MIN_SCORE are
# rejected with a generic "couldn't verify" form error.
RECAPTCHA_SITE_KEY = os.environ.get(
    "RECAPTCHA_SITE_KEY",
    "6Leel9wsAAAAAOCRw7b0t5Gj939fy8fy25ZFRXnU",
)
RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY", "")
RECAPTCHA_MIN_SCORE = float(os.environ.get("RECAPTCHA_MIN_SCORE", "0.5"))

# --- Blog publishing API ---
# Bearer token used to authenticate POST/PUT/PATCH/DELETE on /api/blog/posts/.
# Empty in dev unless set; the API responds 503 if no key is configured so
# misconfigured production is loud, not silent.
LUMA_BLOG_API_KEY = os.environ.get("LUMA_BLOG_API_KEY", "")

# --- Site metadata (used by templates) ---
SITE_NAME = "Luma Tech Solutions"
SITE_BRAND = "Luma Tech"  # shorter form for page titles
SITE_URL = os.environ.get("SITE_URL", "https://lumatechsolutions.co.uk")
SITE_TAGLINE = "Technology that works. Support that lasts."
SITE_PHONE = os.environ.get("SITE_PHONE", "07500 776311")
SITE_PHONE_E164 = os.environ.get("SITE_PHONE_E164", "+447500776311")
SITE_EMAIL = os.environ.get("SITE_EMAIL", "hello@lumatechsolutions.co.uk")
SITE_REGION = "the Thames Valley"
SITE_TOWNS = [
    "Marlow",
    "Maidenhead",
    "Henley-on-Thames",
    "Beaconsfield",
    "Bourne End",
    "Cookham",
    "High Wycombe",
]
SITE_COUNTIES = ["Buckinghamshire", "Berkshire"]
SITE_TOWNS_DISPLAY = (
    "Marlow, Maidenhead, Henley-on-Thames, Beaconsfield, "
    "Bourne End, Cookham and High Wycombe"
)
SITE_FOUNDER = "Marco Baldanza"
SITE_BASE_TOWN = "Marlow"
# Bump when you ship a meaningful site-wide content change so the
# static-page sitemap honestly reflects freshness.
SITE_STATIC_LASTMOD = "2026-05-04"

# --- Security in production ---
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "SAMEORIGIN"
