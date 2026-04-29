import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ContactForm
from .models import BlogPost

log = logging.getLogger(__name__)


PILLARS = [
    {
        "key": "networking",
        "title": "Wi-Fi & Networking",
        "tagline": "Properly engineered Wi-Fi and network design — no more dead-spots, no more rebooting the router.",
        "url_name": "service_networking",
        "icon": "wifi",
    },
    {
        "key": "security",
        "title": "Security",
        "tagline": "CCTV, access control, alarms and smart locks — plus the network protection most installers skip.",
        "url_name": "service_security",
        "icon": "lock",
    },
    {
        "key": "development",
        "title": "App & Web Development",
        "tagline": "Custom websites, web applications and mobile apps — built and supported by the same engineer.",
        "url_name": "service_development",
        "icon": "code",
    },
    {
        "key": "automation",
        "title": "Home Automation",
        "tagline": "Smart homes that are private, fast and keep working when the internet doesn't.",
        "url_name": "service_automation",
        "icon": "home",
    },
    {
        "key": "support",
        "title": "Support & Maintenance",
        "tagline": "Ongoing care so you never have to troubleshoot your own house alone.",
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
            "Automated network monitoring with alerts",
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
            "Same-day response during business hours",
            "Phone & video support",
            "Quarterly check-in call",
            "One annual on-site visit included",
            "Minor smart-home tweaks included",
        ],
    },
    {
        "name": "Enterprise",
        "price_monthly": 149,
        "tagline": "For setups that need priority attention and regular hands-on care.",
        "highlighted": False,
        "features": [
            "Everything in Professional",
            "Priority response — front of the queue",
            "Monthly check-in call",
            "Quarterly on-site visit included",
            "Best-effort out-of-hours for genuine emergencies",
            "Full documentation of your setup, kept up to date",
        ],
    },
]


CASE_STUDIES = [
    {
        "slug": "chiltern-view",
        "title": "Chiltern View — full smart home and UniFi network",
        "summary": (
            "A complete residential rebuild: fast Wi-Fi everywhere, Protect "
            "CCTV recording at the property, and Home Assistant running "
            "scenes, climate, lighting and access — all on a single dashboard "
            "that doesn't depend on anyone's cloud. Aerial drone documentation "
            "is included with every project we deliver."
        ),
        "stack": ["UniFi Dream Machine Pro", "UniFi APs & Switches", "UniFi Protect", "Home Assistant", "Zigbee"],
        "outcome": "Whole-home coverage, automations that work without the internet, no cloud lock-in.",
        "featured": True,
    },
    {
        "slug": "for-sale-by-owner",
        "title": "For Sale By Owner — property listings mobile app",
        "summary": (
            "A polished cross-platform mobile app for a UK property listings "
            "business, with photo uploads, map-based search and a back-office "
            "for the team to moderate listings."
        ),
        "stack": ["React Native (Expo)", "Django REST Framework", "PostgreSQL", "S3-compatible storage"],
        "outcome": "Shipped on iOS and Android in under 12 weeks. Live and supported.",
        "featured": False,
    },
    {
        "slug": "littlewick-house",
        "title": "LittleWick House — whole-property UniFi network",
        "summary": (
            "A large residential property in Maidenhead across four floors, "
            "plus a cellar, garage and separate annex. Eleven access points, "
            "three distribution switches, a Dream Machine Pro at the core, "
            "and three VLANs separating home, IoT and guest traffic — all "
            "on a single managed network with no dead spots."
        ),
        "stack": [
            "UniFi Dream Machine Pro",
            "Pro Max 24 PoE Switch",
            "11× U7-Pro / U7-Pro-Wall APs",
            "3× PoE Switches",
            "VLAN segmentation",
        ],
        "outcome": "Rock-solid Wi-Fi from loft to cellar to annex, with proper network segmentation and room to grow.",
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
                "Everything we offer: Wi-Fi & networking, security, "
                "app & web development, home automation, and ongoing support."
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


def service_security(request):
    return render(
        request,
        "services/security.html",
        _base_context(
            active="security",
            page_title="Security — Luma Tech Solutions",
            page_description=(
                "Physical and cyber security designed, installed and "
                "monitored as one integrated system. UniFi Protect CCTV, "
                "access control, intruder alarms, smart locks and "
                "network hardening."
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
                "Selected case studies: Chiltern View smart home, LittleWick "
                "House whole-property network, For Sale By Owner mobile app, "
                "Paws 4 Thought Dogs website."
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
    posts = BlogPost.published.all()
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "blog/list.html",
        _base_context(
            active="blog",
            page_title="Blog — Luma Tech Solutions",
            page_description=(
                "Practical write-ups on networking, security, smart-home "
                "automation and software, from Luma Tech Solutions in "
                "Berkshire & Buckinghamshire."
            ),
            page_obj=page_obj,
            posts=page_obj.object_list,
        ),
    )


def blog_post(request, slug):
    post = get_object_or_404(BlogPost.published, slug=slug)
    related = (
        BlogPost.published.filter(pillar=post.pillar)
        .exclude(pk=post.pk)[:3]
    )
    return render(
        request,
        "blog/detail.html",
        _base_context(
            active="blog",
            page_title=f"{post.title} — Luma Tech Solutions",
            page_description=post.seo_description,
            post=post,
            related=related,
        ),
    )


def healthz(request):
    return HttpResponse("ok\n", content_type="text/plain")
