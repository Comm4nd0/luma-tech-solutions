from django.conf import settings


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
        "RECAPTCHA_SITE_KEY": settings.RECAPTCHA_SITE_KEY,
    }
