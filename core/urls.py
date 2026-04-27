from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services_overview, name="services"),
    path("services/networking/", views.service_networking, name="service_networking"),
    path("services/development/", views.service_development, name="service_development"),
    path("services/automation/", views.service_automation, name="service_automation"),
    path("services/support/", views.service_support, name="service_support"),
    path("about/", views.about, name="about"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("pricing/", views.pricing, name="pricing"),
    path("contact/", views.contact, name="contact"),
    path("contact/thanks/", views.contact_thanks, name="contact_thanks"),
    path("blog/", views.blog, name="blog"),
    path("healthz", views.healthz, name="healthz"),
]
