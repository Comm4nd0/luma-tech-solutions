from django.urls import path
from django.views.generic import TemplateView

from . import api, views
from .feeds import BlogFeed

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services_overview, name="services"),
    path("services/networking/", views.service_networking, name="service_networking"),
    path("services/security/", views.service_security, name="service_security"),
    path("services/development/", views.service_development, name="service_development"),
    path("services/automation/", views.service_automation, name="service_automation"),
    path("services/support/", views.service_support, name="service_support"),
    path("about/", views.about, name="about"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("areas/", views.areas_index, name="areas"),
    path("areas/marlow/", views.area_marlow, name="area_marlow"),
    path("areas/maidenhead/", views.area_maidenhead, name="area_maidenhead"),
    path("areas/henley/", views.area_henley, name="area_henley"),
    path("contact/", views.contact, name="contact"),
    path("contact/thanks/", views.contact_thanks, name="contact_thanks"),
    path("blog/", views.blog, name="blog"),
    path("blog/feed/", BlogFeed(), name="blog_feed"),
    path("blog/<slug:slug>/", views.blog_post, name="blog_post"),
    path("api/blog/posts/", api.posts_collection, name="api_blog_posts"),
    path("api/blog/posts/<slug:slug>/", api.post_detail, name="api_blog_post"),
    path("healthz", views.healthz, name="healthz"),
]
