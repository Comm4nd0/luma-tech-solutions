from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return [
            ("home", 1.0),
            ("services", 0.9),
            ("service_networking", 0.8),
            ("service_development", 0.8),
            ("service_automation", 0.8),
            ("service_support", 0.8),
            ("about", 0.7),
            ("portfolio", 0.8),
            ("pricing", 0.8),
            ("contact", 0.7),
            ("blog", 0.5),
        ]

    def location(self, item):
        name, _priority = item
        return reverse(name)

    def priority(self, item):
        _name, priority = item
        return priority
