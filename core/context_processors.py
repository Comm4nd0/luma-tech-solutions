from django.conf import settings


def site(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_URL": settings.SITE_URL,
        "SITE_TAGLINE": settings.SITE_TAGLINE,
        "SITE_PHONE": settings.SITE_PHONE,
        "SITE_EMAIL": settings.SITE_EMAIL,
        "SITE_REGION": settings.SITE_REGION,
    }
