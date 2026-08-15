from datetime import date, datetime, time

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from .content import CASE_STUDIES
from .models import BlogPost


def _static_lastmod():
    """Parse SITE_STATIC_LASTMOD into a tz-aware datetime for the sitemap."""
    raw = settings.SITE_STATIC_LASTMOD
    d = date.fromisoformat(raw)
    return timezone.make_aware(datetime.combine(d, time.min))


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
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
            ("area_marlow", 0.8),
            ("area_maidenhead", 0.8),
            ("area_henley", 0.8),
            ("area_beaconsfield", 0.8),
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
        return _static_lastmod()


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
