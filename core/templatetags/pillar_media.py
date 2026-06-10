"""Pillar-keyed photography for blog posts and marketing pages.

Blog posts store their body as HTML; when a post embeds its own <img> we use
that (see BlogPost.first_image). When it doesn't, we fall back to a relevant
photo chosen by the post's pillar, rather than an abstract illustration.

Photos are self-hosted under static/img/services/ (previously these were
hot-linked from the Pexels CDN — slow, third-party, and a single point of
failure). Callers layer a gradient behind them so a failed load degrades to
a colour wash rather than a broken image.
"""
from django import template
from django.templatetags.static import static

register = template.Library()

# pillar / slide key -> static path
_PILLAR_PHOTOS = {
    "networking": "img/services/networking.jpg",   # patched ethernet on a switch
    "security": "img/services/security.jpg",       # CCTV camera
    "development": "img/services/development.jpg", # source code on screen
    "automation": "img/services/automation.jpg",   # smart-home control
    "support": "img/services/support.jpg",         # field engineer with a laptop
    "general": "img/services/networking.jpg",
    "hero": "img/services/support.jpg",            # home-hero: laptop in a bright living room
}


@register.simple_tag
def pillar_photo(pillar, width=1200):
    """Return the static URL for a pillar's photo.

    ``width`` is accepted for backwards compatibility with existing template
    calls (it selected a CDN render size when these were hot-linked); the
    self-hosted originals are 1600px and WhiteNoise serves them cached.
    """
    path = _PILLAR_PHOTOS.get((pillar or "").lower(), _PILLAR_PHOTOS["general"])
    return static(path)
