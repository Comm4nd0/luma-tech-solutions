from django.conf import settings
from django.urls import reverse

from .content import AREA_PAGES


def _area_links():
    """Town pages for the sitewide footer.

    /areas/marlow/ had exactly one inbound link outside the area cluster —
    "Areas we cover" on the footer, pointing at /areas/ rather than at any
    town. A sitewide link per town is the single highest-value fix available.
    """
    return [
        {"url": reverse(page["url_name"]), "town": page["town"]}
        for page in AREA_PAGES.values()
    ]


def site(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_BRAND": settings.SITE_BRAND,
        "SITE_URL": settings.SITE_URL,
        "SITE_TAGLINE": settings.SITE_TAGLINE,
        "SITE_PHONE": settings.SITE_PHONE,
        "SITE_PHONE_E164": settings.SITE_PHONE_E164,
        "SITE_EMAIL": settings.SITE_EMAIL,
        "SITE_REGION": settings.SITE_REGION,
        "SITE_TOWNS": settings.SITE_TOWNS,
        "SITE_COUNTIES": settings.SITE_COUNTIES,
        "SITE_TOWNS_DISPLAY": settings.SITE_TOWNS_DISPLAY,
        "SITE_FOUNDER": settings.SITE_FOUNDER,
        "SITE_BASE_TOWN": settings.SITE_BASE_TOWN,
        "SITE_WHATSAPP_E164": settings.SITE_WHATSAPP_E164,
        "SITE_LINKEDIN": settings.SITE_LINKEDIN,
        "SITE_AREA_LINKS": _area_links(),
        "SITE_BOOKING_URL": settings.SITE_BOOKING_URL,
        "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
        "PLAUSIBLE_DOMAIN": settings.PLAUSIBLE_DOMAIN,
        "PLAUSIBLE_SCRIPT_SRC": settings.PLAUSIBLE_SCRIPT_SRC,
    }
