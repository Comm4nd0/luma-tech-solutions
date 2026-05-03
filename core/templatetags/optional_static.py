"""Template tag for optional static files that may not exist yet.

The site uses ManifestStaticFilesStorage in production, so {% static 'foo' %}
raises ValueError if 'foo' isn't in the manifest. That's the right default
for typos in CSS/JS/etc — but for placeholder photo slots that get filled
in over time (e.g. install photos dropped onto the server later), we want
the page to render with the slot empty rather than 500.

Usage:

    {% load optional_static %}
    {% static_optional 'img/work/rack.jpg' as photo_url %}
    {% if photo_url %}<img src="{{ photo_url }}" alt="..."/>{% endif %}
"""
from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()


@register.simple_tag
def static_optional(path):
    try:
        return staticfiles_storage.url(path)
    except ValueError:
        return ""
