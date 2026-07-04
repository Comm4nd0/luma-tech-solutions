"""Django settings for the Luma Tech Solutions website."""
from pathlib import Path
import os
import sys

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Keys that must never reach production. The guard below refuses to boot with
# DEBUG off if the secret key was never overridden — a misconfigured deploy
# fails loud instead of running with a publicly-known key.
_INSECURE_SECRET_KEYS = {
    "dev-insecure-key-change-me-please-do-not-use-in-production-xyz123",
    "change-me-in-production",
    "build-only",
    "",
}

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-key-change-me-please-do-not-use-in-production-xyz123",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

if not DEBUG and SECRET_KEY in _INSECURE_SECRET_KEYS:
    raise ImproperlyConfigured(
        "DJANGO_SECRET_KEY is unset or using an insecure default while "
        "DJANGO_DEBUG is off. Generate one with: "
        'python -c "import secrets; print(secrets.token_urlsafe(50))"'
    )

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
    "core.middleware.ContentSecurityPolicyMiddleware",
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
        # WAL lets readers and a writer work concurrently; the longer busy
        # timeout stops "database is locked" errors when the blog API or a
        # form submit collides with another worker writing.
        "OPTIONS": {
            "timeout": 20,
            "init_command": "PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;",
        },
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

# During tests, drop the hashed-manifest static storage so templates using
# {% static %} render without a prior collectstatic.
if "test" in sys.argv:
    STORAGES["staticfiles"]["BACKEND"] = (
        "django.contrib.staticfiles.storage.StaticFilesStorage"
    )

# --- Uploaded media (CVs) ---
# Lives inside the persisted data volume, NOT under STATIC_ROOT, so it is
# never served publicly by WhiteNoise. CVs are downloaded through a
# staff-only admin view. Keeping the file means a failed notification email
# no longer loses the application.
MEDIA_ROOT = Path(os.environ.get("DJANGO_MEDIA_ROOT", BASE_DIR / "data" / "media"))
MEDIA_URL = "/media/"

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
# Falls back to CONTACT_FORM_RECIPIENT — set this if you want job applications
# routed to a separate inbox (e.g. careers@).
CAREERS_FORM_RECIPIENT = (
    os.environ.get("CAREERS_FORM_RECIPIENT") or CONTACT_FORM_RECIPIENT
)

# CV uploads can run to ~5 MB. Django's default 2.5 MB cap on POST body and
# in-memory upload would reject those, so bump both ceilings to 6 MB.
DATA_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 6 * 1024 * 1024

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
SITE_STATIC_LASTMOD = "2026-07-04"

# --- Commercial / B2B links ---
# LinkedIn profile URL. When set, appears in the footer and in the
# Organization sameAs schema. Empty hides it.
SITE_LINKEDIN = os.environ.get("SITE_LINKEDIN", "")
# Scheduling link (e.g. Calendly) for "book a call" CTAs aimed at
# commercial buyers. Empty falls back to the phone number.
SITE_BOOKING_URL = os.environ.get("SITE_BOOKING_URL", "")

# --- WhatsApp click-to-chat ---
# E.164 format (e.g. +447xxxxxxxxx). Set to empty to hide the floating
# button and the WhatsApp contact options.
SITE_WHATSAPP_E164 = os.environ.get("SITE_WHATSAPP_E164", "+447500776311")

# --- Analytics (cookieless) ---
# When set, drops the Plausible snippet into base.html. Empty disables it.
# The default script src uses Plausible's tagged-events variant so we can
# fire custom events via class="plausible-event-name=..." on any element.
# Swap PLAUSIBLE_SCRIPT_SRC to point at Umami / Fathom / self-hosted Plausible
# if the provider changes; the snippet shape is identical.
PLAUSIBLE_DOMAIN = os.environ.get("PLAUSIBLE_DOMAIN", "")
PLAUSIBLE_SCRIPT_SRC = os.environ.get(
    "PLAUSIBLE_SCRIPT_SRC", "https://plausible.io/js/script.tagged-events.js"
)

# --- Error reporting ---
# Unhandled 500s are emailed to ADMINS (requires a real email backend). Set
# DJANGO_ADMINS to a comma-separated list of addresses; SERVER_EMAIL is the
# From address for those error mails.
ADMINS = [
    ("Luma Tech", addr.strip())
    for addr in os.environ.get("DJANGO_ADMINS", "").split(",")
    if addr.strip()
]
MANAGERS = ADMINS
SERVER_EMAIL = os.environ.get("DJANGO_SERVER_EMAIL") or DEFAULT_FROM_EMAIL

# --- Logging ---
# Without an explicit config Django only surfaces WARNING+ from the `django`
# logger, so our log.info() calls (reCAPTCHA rejections, etc.) never appear.
# Route the app's own loggers to the console at INFO and mail unhandled
# request errors to ADMINS.
LOG_LEVEL = os.environ.get("DJANGO_LOG_LEVEL", "INFO")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "class": "django.utils.log.AdminEmailHandler",
            "level": "ERROR",
            "include_html": True,
        },
    },
    "root": {"handlers": ["console"], "level": "WARNING"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "core": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
    },
}

# --- Content Security Policy ---
# Enforced by core.middleware.ContentSecurityPolicyMiddleware (nonce-based).
# Flip DJANGO_CSP_REPORT_ONLY=1 to emit the report-only header instead —
# useful when introducing a new third-party script before enforcing it.
CSP_REPORT_ONLY = os.environ.get("DJANGO_CSP_REPORT_ONLY", "0") == "1"

# --- Security in production ---
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    X_FRAME_OPTIONS = "SAMEORIGIN"
