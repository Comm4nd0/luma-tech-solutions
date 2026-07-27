"""Deploy-time configuration checks.

These run under ``manage.py check --deploy`` (and so in CI). They are
Warnings, not Errors, deliberately: ``check`` exits non-zero on errors, and
CI runs the deploy check without any email or reCAPTCHA environment set.
The point is to make a production misconfiguration loud in the deploy log,
not to make the build unrunnable.
"""

from django.conf import settings
from django.core.checks import Warning, register

SILENT_BACKENDS = (
    "django.core.mail.backends.console.EmailBackend",
    "django.core.mail.backends.dummy.EmailBackend",
    "django.core.mail.backends.locmem.EmailBackend",
)


@register(deploy=True)
def email_delivery_configured(app_configs, **kwargs):
    """Leads are only useful if they actually leave the container."""
    if settings.DEBUG:
        return []

    issues = []
    if settings.EMAIL_BACKEND in SILENT_BACKENDS:
        issues.append(
            Warning(
                "Email backend %s discards mail." % settings.EMAIL_BACKEND,
                hint=(
                    "Contact, quote and careers submissions will be written to "
                    "container stdout and marked notified=True, so lead loss is "
                    "silent. Set DJANGO_EMAIL_BACKEND to the SMTP backend."
                ),
                id="core.W001",
            )
        )
    elif not settings.EMAIL_HOST:
        issues.append(
            Warning(
                "EMAIL_HOST is empty but the SMTP backend is configured.",
                hint="Set DJANGO_EMAIL_HOST (and the matching credentials).",
                id="core.W002",
            )
        )

    if not settings.CONTACT_FORM_RECIPIENT:
        issues.append(
            Warning(
                "CONTACT_FORM_RECIPIENT is empty — nobody receives leads.",
                id="core.W003",
            )
        )
    return issues


@register(deploy=True)
def recaptcha_configured(app_configs, **kwargs):
    """An empty secret key silently disables verification on every form."""
    if settings.DEBUG or settings.RECAPTCHA_SECRET_KEY:
        return []
    return [
        Warning(
            "RECAPTCHA_SECRET_KEY is empty — reCAPTCHA verification is skipped.",
            hint=(
                "The public contact, quote and careers forms fall back to the "
                "honeypot alone. Set RECAPTCHA_SECRET_KEY in production."
            ),
            id="core.W004",
        )
    ]
