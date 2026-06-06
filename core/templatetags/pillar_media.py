"""Pillar-keyed stock photography for blog posts and the home hero.

Blog posts store their body as HTML; when a post embeds its own <img> we use
that (see BlogPost.first_image). When it doesn't, we fall back to a relevant
stock photo chosen by the post's pillar, rather than an abstract illustration.
The home hero slides reuse the same mapping.

Pexels CDN URLs are hot-linkable and stable; callers layer a gradient behind
them so a failed load degrades to a colour wash rather than a broken image.
"""
from django import template

register = template.Library()

# pillar / slide key -> Pexels photo id
_PILLAR_PHOTOS = {
    "networking": "1054397",   # patched ethernet on a switch
    "security": "558630",      # CCTV camera
    "development": "16592498", # source code on screen
    "automation": "16423104",  # smart-home control
    "support": "442152",       # field engineer with a laptop
    "general": "3184357",      # people working with technology
    "hero": "3184357",         # home-hero flagship slide
}


@register.simple_tag
def pillar_photo(pillar, width=1200):
    pid = _PILLAR_PHOTOS.get((pillar or "").lower(), _PILLAR_PHOTOS["general"])
    return (
        f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"
        f"?auto=compress&cs=tinysrgb&w={width}"
    )
