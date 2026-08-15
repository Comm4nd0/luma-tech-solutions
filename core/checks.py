"""Deploy-time configuration checks.

These run under ``manage.py check --deploy`` (and so in CI). They are
Warnings, not Errors, deliberately: ``check`` exits non-zero on errors, and
CI runs the deploy check without any email or reCAPTCHA environment set.
The point is to make a production misconfiguration loud in the deploy log,
not to make the build unrunnable.
"""

from django.conf import settings
from django.core.checks import Warning, register

from .content import AREA_PAGES, area_is_draft, area_placeholder_fields

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
def area_pages_have_local_detail(app_configs, **kwargs):
    """Town pages must carry real local copy before they are worth indexing.

    A page whose only difference from its neighbours is the town name is a
    doorway page. This does not fail the build: a page listed here is already
    being served noindex and kept out of sitemap.xml (see
    ``content.area_is_draft``), so the failure mode is a page nobody sees
    rather than a page Google penalises.
    """
    issues = []
    for key, page in AREA_PAGES.items():
        outstanding = area_placeholder_fields(page)
        if not outstanding:
            continue
        state = (
            "noindex and excluded from sitemap.xml"
            if area_is_draft(page)
            else "indexed, but thinner than it should be"
        )
        issues.append(
            Warning(
                "Area page '%s' still has placeholder copy in: %s — it is %s."
                % (key, ", ".join(outstanding), state),
                hint=(
                    "Write the real copy in core/content.py AREA_PAGES['%s']. "
                    "example_jobs placeholders are dropped from the rendered "
                    "page rather than published, so the page currently shows "
                    "no local proof. Do not invent jobs to clear this." % key
                ),
                id="core.W005",
            )
        )
    return issues


@register(deploy=True)
def local_business_entity_configured(app_configs, **kwargs):
    """The JSON-LD should link out to profiles proving which company we are.

    A same-named LED company in Burnaby BC outranks this site for its own
    brand, so ``sameAs`` is doing entity disambiguation, not decoration.

    This deliberately does NOT ask for a street address, postcode or geo
    point. Luma Tech is a service-area business with no premises a client
    would visit, and a schema address that contradicts a service-area Google
    Business Profile is a weaker signal than no address at all. Locality,
    region and country are always emitted and are the correct level of
    detail here.
    """
    if getattr(settings, "SITE_GOOGLE_BUSINESS_URL", ""):
        return []
    return [
        Warning(
            "SITE_GOOGLE_BUSINESS_URL is unset — the JSON-LD sameAs list "
            "has no Google Business Profile in it.",
            hint=(
                "Set it in lumatech/settings.py (or the environment) to the "
                "maps.google.com/maps/place/… or maps.app.goo.gl/… URL for "
                "the profile — not the g.page/r/…/review shortlink. Adding a "
                "Companies House URL to SITE_EXTRA_SAME_AS is the other "
                "high-value signal that this is the UK company."
            ),
            id="core.W006",
        )
    ]


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
