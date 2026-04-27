import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ContactForm

log = logging.getLogger(__name__)


PILLARS = [
    {
        "key": "networking",
        "title": "Wi-Fi & Networking",
        "tagline": "Enterprise-grade network design and installation using Ubiquiti UniFi.",
        "url_name": "service_networking",
        "icon": "wifi",
    },
    {
        "key": "development",
        "title": "App & Web Development",
        "tagline": "Custom mobile apps, websites, and web applications.",
        "url_name": "service_development",
        "icon": "code",
    },
    {
        "key": "automation",
        "title": "Home Automation",
        "tagline": "Smart home design using Home Assistant — local, fast, private.",
        "url_name": "service_automation",
        "icon": "home",
    },
    {
        "key": "support",
        "title": "Support & Maintenance",
        "tagline": "Ongoing care plans so you never troubleshoot alone.",
        "url_name": "service_support",
        "icon": "shield",
    },
]


TESTIMONIALS = [
    {
        "name": "Helen R.",
        "role": "Owner, Chiltern View",
        "rating": 5,
        "quote": (
            "Marco redesigned our Wi-Fi and built a full smart home setup. "
            "Everything just works — and when we need a tweak he's a message away."
        ),
    },
    {
        "name": "James T.",
        "role": "Co-founder, For Sale By Owner",
        "rating": 5,
        "quote": (
            "Luma Tech delivered our mobile app on time and on budget. "
            "Clean code, sensible advice, and a partner who actually understands the business."
        ),
    },
    {
        "name": "Sarah M.",
        "role": "Paws 4 Thought Dogs",
        "rating": 5,
        "quote": (
            "Beautiful website, fast turnaround, and ongoing support. "
            "I never feel like I'm bothering them — they treat the site like it's their own."
        ),
    },
]


CARE_PLANS = [
    {
        "name": "Essential",
        "price_monthly": 29,
        "tagline": "Peace of mind for homes and small offices.",
        "highlighted": False,
        "features": [
            "24/7 remote network monitoring",
            "Email support, next-business-day response",
            "Quarterly health-check report",
            "Firmware & security updates managed for you",
            "Discounted on-site call-out rate",
        ],
    },
    {
        "name": "Professional",
        "price_monthly": 59,
        "tagline": "For households and businesses that depend on tech.",
        "highlighted": True,
        "features": [
            "Everything in Essential",
            "Priority 4-hour response, business hours",
            "Phone & video support",
            "Monthly check-in call",
            "One annual on-site visit included",
            "Smart-home automation tweaks included",
        ],
    },
    {
        "name": "Enterprise",
        "price_monthly": 149,
        "tagline": "Mission-critical, with SLAs in writing.",
        "highlighted": False,
        "features": [
            "Everything in Professional",
            "2-hour response SLA",
            "Dedicated account manager",
            "Quarterly on-site visit included",
            "Out-of-hours emergency support",
            "Documented runbook for your stack",
        ],
    },
]


CASE_STUDIES = [
    {
        "slug": "chiltern-view",
        "title": "Chiltern View — full smart home + UniFi network",
        "summary": (
            "A complete residential rebuild: UniFi Wi-Fi 6E across the property, "
            "Protect CCTV, Home Assistant running scenes, climate, lighting and "
            "access — all on a single, locally-controlled stack."
        ),
        "stack": ["UniFi Dream Machine Pro", "UniFi APs & Switches", "UniFi Protect", "Home Assistant", "Zigbee2MQTT"],
        "outcome": "Whole-home coverage, local-first automation, zero cloud lock-in.",
        "featured": True,
    },
    {
        "slug": "for-sale-by-owner",
        "title": "For Sale By Owner — property listings mobile app",
        "summary": (
            "A native-quality cross-platform mobile app for a UK property "
            "listings business, with photo upload, geo-search, and an admin "
            "back-office for moderation."
        ),
        "stack": ["React Native (Expo)", "Django REST Framework", "PostgreSQL", "S3-compatible storage"],
        "outcome": "Shipped iOS & Android in under 12 weeks. Live in production.",
        "featured": False,
    },
    {
        "slug": "paws-4-thought-dogs",
        "title": "Paws 4 Thought Dogs — small business website",
        "summary": (
            "A polished, SEO-friendly website for a local dog-walking business, "
            "with booking enquiries, gallery and Google Business integration."
        ),
        "stack": ["Static site", "Custom CSS", "Caddy + Docker", "Hetzner VPS"],
        "outcome": "First-page Google ranking for local search within 6 weeks.",
        "featured": False,
    },
]


def _base_context(active=None, **extra):
    ctx = {
        "active_nav": active,
        "pillars": PILLARS,
    }
    ctx.update(extra)
    return ctx


def home(request):
    featured = next((c for c in CASE_STUDIES if c["featured"]), CASE_STUDIES[0])
    return render(
        request,
        "home.html",
        _base_context(
            active="home",
            page_title=f"{settings.SITE_NAME} — {settings.SITE_TAGLINE}",
            page_description=(
                "Professional networking, development, automation and support "
                "for homes and businesses across Berkshire & Buckinghamshire."
            ),
            testimonials=TESTIMONIALS,
            featured_case=featured,
        ),
    )


def services_overview(request):
    return render(
        request,
        "services/overview.html",
        _base_context(
            active="services",
            page_title=f"Services — {settings.SITE_NAME}",
            page_description=(
                "Four pillars of service: Wi-Fi & networking, app & web "
                "development, home automation, and ongoing support."
            ),
        ),
    )


def service_networking(request):
    return render(
        request,
        "services/networking.html",
        _base_context(
            active="services",
            page_title="Wi-Fi & Networking — Luma Tech Solutions",
            page_description=(
                "Enterprise-grade UniFi Wi-Fi and networking design, "
                "installation and management. From £800."
            ),
        ),
    )


def service_development(request):
    return render(
        request,
        "services/development.html",
        _base_context(
            active="services",
            page_title="App & Web Development — Luma Tech Solutions",
            page_description=(
                "Custom mobile apps, websites and web applications, built by "
                "an engineer who actually ships and supports what they build."
            ),
        ),
    )


def service_automation(request):
    return render(
        request,
        "services/automation.html",
        _base_context(
            active="services",
            page_title="Home Automation — Luma Tech Solutions",
            page_description=(
                "Local-first smart-home design with Home Assistant. Lighting, "
                "climate, security, scenes — privately, reliably."
            ),
        ),
    )


def service_support(request):
    return render(
        request,
        "services/support.html",
        _base_context(
            active="services",
            page_title="Support & Care Plans — Luma Tech Solutions",
            page_description=(
                "Three care-plan tiers — Essential (£29), Professional (£59) "
                "and Enterprise (£149). Monitoring, response SLAs, and a "
                "human on the other end of the phone."
            ),
            care_plans=CARE_PLANS,
        ),
    )


def about(request):
    return render(
        request,
        "about.html",
        _base_context(
            active="about",
            page_title="About — Luma Tech Solutions",
            page_description=(
                "Founded by Marco Baldanza, an engineer with a background in "
                "enterprise infrastructure and software. Based in Berkshire & "
                "Buckinghamshire."
            ),
        ),
    )


def portfolio(request):
    return render(
        request,
        "portfolio.html",
        _base_context(
            active="portfolio",
            page_title="Portfolio — Luma Tech Solutions",
            page_description=(
                "Selected case studies: Chiltern View smart home, For Sale By "
                "Owner mobile app, Paws 4 Thought Dogs website."
            ),
            case_studies=CASE_STUDIES,
        ),
    )


def pricing(request):
    return render(
        request,
        "pricing.html",
        _base_context(
            active="pricing",
            page_title="Pricing — Luma Tech Solutions",
            page_description=(
                "Transparent pricing across networking, development, "
                "automation and support. No surprises, no day rates hidden "
                "behind a ‘call us’ button."
            ),
            care_plans=CARE_PLANS,
        ),
    )


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save()
            try:
                send_mail(
                    subject=f"[Luma Tech] New enquiry from {submission.name}",
                    message=(
                        f"Name:    {submission.name}\n"
                        f"Email:   {submission.email}\n"
                        f"Phone:   {submission.phone or '—'}\n"
                        f"Service: {submission.get_service_display()}\n"
                        f"\n"
                        f"{submission.message}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_FORM_RECIPIENT],
                    fail_silently=False,
                )
                submission.notified = True
                submission.save(update_fields=["notified"])
            except Exception:
                log.exception("Failed to send contact notification email")
            messages.success(request, "Thanks — we'll be in touch shortly.")
            return redirect(reverse("contact_thanks"))
    else:
        form = ContactForm()

    return render(
        request,
        "contact.html",
        _base_context(
            active="contact",
            page_title="Contact — Luma Tech Solutions",
            page_description=(
                "Get in touch about networking, development, automation or "
                "support. We cover Berkshire, Buckinghamshire and the "
                "surrounding area."
            ),
            form=form,
        ),
    )


def contact_thanks(request):
    return render(
        request,
        "contact_thanks.html",
        _base_context(
            active="contact",
            page_title="Thanks — Luma Tech Solutions",
            page_description="Your enquiry has been received.",
        ),
    )


def blog(request):
    return render(
        request,
        "blog.html",
        _base_context(
            active="blog",
            page_title="Blog — Luma Tech Solutions",
            page_description="Notes from the workshop. Coming soon.",
        ),
    )


def healthz(request):
    return HttpResponse("ok\n", content_type="text/plain")
