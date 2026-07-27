from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from core.sitemaps import BlogPostSitemap, CaseStudySitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "cases": CaseStudySitemap,
    "blog": BlogPostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    # Safe to cache: no CSP nonce, no CSRF token, no messages. Saves a
    # BlogPost query plus 23 reverse() calls on every crawler hit.
    path(
        "sitemap.xml",
        cache_page(3600)(sitemap),
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="robots.txt", content_type="text/plain"
        ),
        name="robots",
    ),
    path("", include("core.urls")),
]
