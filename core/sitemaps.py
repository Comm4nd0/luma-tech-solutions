from datetime import date, datetime, time

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .content import AREA_PAGES, CASE_STUDIES, PAGE_LASTMOD, area_is_draft
from .models import BlogPost

# URL names of area pages still carrying placeholder copy. They are served and
# linked but noindexed, so listing them in the sitemap would be asking Google
# to index a page we have just told it not to.
DRAFT_AREA_URL_NAMES = frozenset(
    page["url_name"] for page in AREA_PAGES.values() if area_is_draft(page)
)


def _as_datetime(raw):
    """Parse an ISO date string into a tz-aware datetime for the sitemap."""
    return timezone.make_aware(datetime.combine(date.fromisoformat(raw), time.min))


def _static_lastmod(url_name=None):
    """Last-modified for a static page.

    Every static page used to report SITE_STATIC_LASTMOD, so the sitemap told
    Google that /privacy/ and /areas/marlow/ were touched on the same day,
    every day — no signal at all. PAGE_LASTMOD carries a real date for the
    pages that actually change; SITE_STATIC_LASTMOD remains the floor.
    """
    return _as_datetime(PAGE_LASTMOD.get(url_name, settings.SITE_STATIC_LASTMOD))


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return [
            entry for entry in self._all_items()
            if entry[0] not in DRAFT_AREA_URL_NAMES
        ]

    def _all_items(self):
        return [
            ("home", 1.0),
            ("quote", 0.95),
            ("services", 0.9),
            ("service_networking", 0.8),
            ("service_security", 0.8),
            ("service_cctv", 0.85),
            ("service_access_control", 0.75),
            ("service_alarms", 0.75),
            ("service_ai_cameras", 0.85),
            ("construction", 0.9),
            ("camera_privacy", 0.6),
            ("service_development", 0.8),
            ("service_automation", 0.8),
            ("service_support", 0.8),
            ("areas", 0.7),
            ("area_marlow", 0.85),
            ("area_maidenhead", 0.85),
            ("area_henley", 0.85),
            ("area_beaconsfield", 0.85),
            ("area_high_wycombe", 0.85),
            ("about", 0.7),
            ("portfolio", 0.8),
            ("contact", 0.7),
            ("careers", 0.6),
            ("blog", 0.5),
            ("terms", 0.3),
            ("privacy", 0.3),
        ]

    def location(self, item):
        name, _priority = item
        return reverse(name)

    def priority(self, item):
        _name, priority = item
        return priority

    def lastmod(self, item):
        name, _priority = item
        return _static_lastmod(name)


class CaseStudySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7
    protocol = "https"

    def items(self):
        return [c["slug"] for c in CASE_STUDIES]

    def location(self, slug):
        return reverse("case_study", args=[slug])

    def lastmod(self, slug):
        return _static_lastmod()


class BlogPostSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    protocol = "https"

    def items(self):
        return BlogPost.published.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
