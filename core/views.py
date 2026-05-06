import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ContactForm
from .models import BlogPost, SERVICE_CHOICES

log = logging.getLogger(__name__)


def _verify_recaptcha(token, remote_ip=""):
    """Verify a reCAPTCHA v3 token with Google. Returns (passed, score, reason).

    When RECAPTCHA_SECRET_KEY is unset (local dev), verification is skipped
    and (True, 1.0, "skipped") is returned so the form still works.
    """
    if not settings.RECAPTCHA_SECRET_KEY:
        return True, 1.0, "skipped (no secret configured)"
    if not token:
        return False, 0.0, "missing token"
    try:
        data = urllib.parse.urlencode(
            {
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": token,
                "remoteip": remote_ip,
            }
        ).encode()
        req = urllib.request.Request(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read().decode())
    except Exception as exc:
        log.warning("reCAPTCHA verification network error: %s", exc)
        return False, 0.0, "verification error"

    score = float(result.get("score", 0.0))
    if not result.get("success"):
        codes = ",".join(result.get("error-codes", [])) or "unknown"
        return False, score, codes
    if score < settings.RECAPTCHA_MIN_SCORE:
        return False, score, f"low score {score:.2f}"
    return True, score, "ok"


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
        "name": "Claire M.",
        "role": "Paws 4 Thought Dogs",
        "rating": 5,
        "quote": (
            "Beautiful website, fast turnaround, and ongoing support. "
            "I never feel like I'm bothering them — they treat the site like it's their own."
        ),
    },
]


HOME_CARE_PLANS = [
    {
        "name": "Essential",
        "price": "£75",
        "price_suffix": "/mo +VAT",
        "annual_price": "£810",
        "annual_suffix": "/yr",
        "min_term": "3-month rolling",
        "tagline": "Quiet, reliable IT — we watch it, you forget about it.",
        "highlighted": False,
        "features": [
            "24/7 automated network monitoring with alerts to us",
            "Firmware, security patches and daily config backups managed for you",
            "Email support — next business day for routine, same business day (best effort) for service-down",
            "Quarterly health-check report",
            "One-page network diagram, kept current with any changes we make",
            "20% off our standard hourly rate for work outside the plan",
            "Internet provider liaison when your line goes down — we make the calls",
        ],
    },
    {
        "name": "Professional",
        "price": "£165",
        "price_suffix": "/mo +VAT",
        "annual_price": "£1,780",
        "annual_suffix": "/yr",
        "min_term": "6-month rolling",
        "tagline": "Hands-on support for everything Luma installed — same engineer who built it.",
        "highlighted": True,
        "features": [
            "Everything in Essential",
            "Reactive support for any kit, app or integration we supplied or installed — networking, CCTV, smart-home, custom apps",
            "Same business day for routine; target within 4 working hours for service-down",
            "Phone, video and WhatsApp support",
            "2 hours of remote moves-and-changes per year (rolls over up to 4)",
            "One on-site visit per year included (tune-up, cable check, hardware audit)",
            "Warranty management on hardware we supply — UI Care registered, RMAs handled by us",
            "5% loyalty discount from year 2",
        ],
    },
    {
        "name": "Concierge",
        "price": "£325",
        "price_suffix": "/mo +VAT",
        "annual_price": "£3,510",
        "annual_suffix": "/yr",
        "min_term": "12-month",
        "tagline": "The whole smart home, whoever installed it — one engineer, one number, one bill.",
        "highlighted": False,
        "features": [
            "Everything in Professional",
            "We'll take a look at any smart-home product in the house, whoever installed it — Sonos, Lutron, Ring, Nest, Hue, legacy integrations. Diagnose, advise and escalate to the manufacturer; we don't warrant kit we didn't supply, but you've got one number to call.",
            "Front of queue; target within 2 working hours for service-down",
            "Best-effort out-of-hours for genuine emergencies",
            "One on-site visit per quarter + monthly check-in call",
            "6 hours of remote moves-and-changes per year (rolls over up to 12)",
            "Full living documentation — network map, device inventory, credentials vault, runbook",
            "Loaner hardware where we have stock; otherwise we expedite the RMA on your behalf",
            "Multi-site coverage — main home plus a holiday let or small office under one plan",
            "10% loyalty discount from year 2",
        ],
    },
]


BUSINESS_CARE_PLANS = [
    {
        "name": "Essential",
        "price": "£25",
        "price_suffix": "/user/mo +VAT",
        "annual_price": "£270",
        "annual_suffix": "/user/yr",
        "min_term": "3-month rolling",
        "tagline": "Quiet, reliable IT for small teams — we watch it, you focus on the work.",
        "highlighted": False,
        "features": [
            "24/7 automated network monitoring with alerts to us",
            "Firmware, security patches and daily config backups managed for you",
            "Email support — next business day for routine, same business day (best effort) for service-down",
            "Quarterly health-check report",
            "One-page network diagram, kept current with any changes we make",
            "20% off our standard hourly rate for work outside the plan",
            "Internet provider liaison when your line goes down — we make the calls",
        ],
    },
    {
        "name": "Professional",
        "price": "£55",
        "price_suffix": "/user/mo +VAT",
        "annual_price": "£595",
        "annual_suffix": "/user/yr",
        "min_term": "6-month rolling",
        "tagline": "Hands-on support for everything Luma installed — same engineer who built it.",
        "highlighted": True,
        "features": [
            "Everything in Essential",
            "Reactive support for any kit, app or integration we supplied or installed — networking, CCTV, point-of-sale, custom apps",
            "Same business day for routine; target within 4 working hours for service-down",
            "Phone, video and WhatsApp support",
            "2 hours of remote moves-and-changes per user per year (rolls over up to 4)",
            "One on-site visit per quarter (cable check, hardware audit, team Q&A)",
            "Warranty management on hardware we supply — UI Care registered, RMAs handled by us",
            "5% loyalty discount from year 2",
        ],
    },
    {
        "name": "Concierge",
        "price": "£110",
        "price_suffix": "/user/mo +VAT",
        "annual_price": "£1,190",
        "annual_suffix": "/user/yr",
        "min_term": "12-month",
        "tagline": "The whole office, whoever installed it — one engineer, one number, one bill.",
        "highlighted": False,
        "features": [
            "Everything in Professional",
            "We'll take a look at any networked product on the premises, whoever installed it — printers, NAS, VOIP, point-of-sale, legacy kit from a previous IT company. Diagnose, advise and escalate to the manufacturer; we don't warrant kit we didn't supply, but you've got one number to call.",
            "Front of queue; target within 2 working hours for service-down",
            "Best-effort out-of-hours for genuine emergencies",
            "One on-site visit per month + monthly check-in call",
            "6 hours of remote moves-and-changes per user per year (rolls over up to 12)",
            "Full living documentation — network map, device inventory, credentials vault, runbook",
            "Loaner hardware where we have stock; otherwise we expedite the RMA on your behalf",
            "Multi-site coverage — main office plus a satellite or warehouse under one plan",
            "10% loyalty discount from year 2",
        ],
    },
]


CASE_STUDIES = [
    {
        "slug": "chiltern-view",
        "title": "Chiltern View — full smart home and UniFi network",
        "tag": "Smart home + networking",
        "illustration": "automation",
        "summary": (
            "A complete residential rebuild: fast Wi-Fi everywhere, Protect "
            "CCTV recording at the property, and Home Assistant running "
            "scenes, climate, lighting and access — all on a single dashboard "
            "that doesn't depend on anyone's cloud."
        ),
        "stack": ["UniFi Dream Machine Pro", "UniFi APs & Switches", "UniFi Protect", "Home Assistant", "Zigbee"],
        "outcome": "Whole-home coverage, automations that work without the internet, no cloud lock-in.",
        "featured": False,
    },
    {
        "slug": "for-sale-by-owner",
        "title": "For Sale By Owner — property listings mobile app",
        "tag": "Mobile app",
        "illustration": "development",
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
        "tag": "Networking",
        "illustration": "networking",
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
        "featured": True,
    },
    {
        "slug": "paws-4-thought-dogs",
        "title": "Paws 4 Thought Dogs — small business website",
        "tag": "Marketing site",
        "illustration": "development",
        "summary": (
            "A polished, SEO-friendly website for a local dog-walking business, "
            "with booking enquiries, gallery and Google Business integration."
        ),
        "stack": ["Static site", "Custom CSS", "Caddy + Docker", "Hetzner VPS"],
        "outcome": "First-page Google ranking for local search within 6 weeks.",
        "featured": False,
    },
    {
        "slug": "paws-4-thought-dogs-app",
        "title": "Paws 4 Thought Dogs — mobile app",
        "tag": "Mobile app",
        "illustration": "development",
        "summary": (
            "A two-sided iOS app for the same Berkshire dog-daycare business. "
            "Owners get a daily photo and video feed of their dogs, book "
            "boarding, manage dog profiles and message staff directly. Staff "
            "get a dashboard for daily assignments, request approvals, "
            "transport tracking and compatibility notes — all synced to a "
            "Django backend with offline-first caching for use in the field."
        ),
        "stack": [
            "Flutter",
            "Django REST Framework",
            "PostgreSQL",
            "Push notifications",
            "Offline cache (Hive)",
        ],
        "outcome": "Live on the App Store. iPhone, iPad, Mac (M1+) and Apple Vision supported.",
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
            page_title="Wi-Fi, CCTV & IT Support — Marlow, Maidenhead & Henley | Luma Tech",
            page_description=(
                "Local engineer for proper Wi-Fi, CCTV, smart homes and IT "
                "support across Marlow, Maidenhead, Henley and the Thames Valley."
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
            page_title="Networking, CCTV, Smart Home & IT Services | Luma Tech",
            page_description=(
                "Wi-Fi design, CCTV, app development, home automation and "
                "ongoing care for homes and small businesses across Bucks and Berks."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
            ],
        ),
    )


def service_networking(request):
    return render(
        request,
        "services/networking.html",
        _base_context(
            active="services",
            page_title="Wi-Fi Installation in Marlow, Maidenhead & Henley | Luma Tech",
            page_description=(
                "UniFi Wi-Fi design and installation for large homes and "
                "offices across Marlow, Maidenhead, Henley and the Thames Valley."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("Wi-Fi & Networking", reverse("service_networking")),
            ],
            service_name="Wi-Fi & Networking",
            service_type="Wi-Fi Installation",
            service_url=reverse("service_networking"),
            service_description=(
                "UniFi Wi-Fi and network design, installation and management "
                "for homes and small businesses across Marlow, Maidenhead, "
                "Henley-on-Thames and the wider Thames Valley."
            ),
        ),
    )


def service_security(request):
    return render(
        request,
        "services/security.html",
        _base_context(
            active="security",
            page_title="CCTV Installation in Marlow, Maidenhead & Henley | Luma Tech",
            page_description=(
                "UniFi Protect CCTV, alarms, smart locks and network security "
                "across Marlow, Maidenhead, Henley-on-Thames and the Thames Valley."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("Security", reverse("service_security")),
            ],
            service_name="Security",
            service_type="CCTV Installation",
            service_url=reverse("service_security"),
            service_description=(
                "UniFi Protect CCTV, access control, alarms, smart locks and "
                "network hardening for homes and businesses across Marlow, "
                "Maidenhead, Beaconsfield and the Thames Valley."
            ),
        ),
    )


def service_development(request):
    return render(
        request,
        "services/development.html",
        _base_context(
            active="services",
            page_title="Mobile App & Website Development | Luma Tech",
            page_description=(
                "Custom websites, web apps and iOS/Android apps built and "
                "supported by one engineer in Marlow, Buckinghamshire."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("App & Web Development", reverse("service_development")),
            ],
            service_name="App & Web Development",
            service_type="Software Development",
            service_url=reverse("service_development"),
            service_description=(
                "Custom websites, web applications and mobile apps built and "
                "supported by an engineer in Marlow, Buckinghamshire."
            ),
        ),
    )


def service_automation(request):
    return render(
        request,
        "services/automation.html",
        _base_context(
            active="services",
            page_title="Smart Home Installer, Marlow & Henley | Luma Tech",
            page_description=(
                "Local-first smart-home design with Home Assistant. Lighting, "
                "climate, security across Marlow, Henley and the Thames Valley."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("Home Automation", reverse("service_automation")),
            ],
            service_name="Home Automation",
            service_type="Home Automation",
            service_url=reverse("service_automation"),
            service_description=(
                "Local-first smart-home design with Home Assistant — lighting, "
                "climate, security and scenes across Marlow, Henley-on-Thames "
                "and the Thames Valley."
            ),
        ),
    )


def service_support(request):
    return render(
        request,
        "services/support.html",
        _base_context(
            active="services",
            page_title="IT Support & Care Plans, Bucks & Berks | Luma Tech",
            page_description=(
                "Three care-plan tiers with monitoring, response SLAs and a "
                "real human. Serving homes and businesses across the Thames Valley."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("Support & Maintenance", reverse("service_support")),
            ],
            service_name="Support & Maintenance",
            service_type="IT Support",
            service_url=reverse("service_support"),
            service_description=(
                "Ongoing IT support and care plans for homes and small "
                "businesses across Marlow, Maidenhead and the Thames Valley."
            ),
            plan_grids=[
                {"audience": "home", "plans": HOME_CARE_PLANS},
                {"audience": "business", "plans": BUSINESS_CARE_PLANS},
            ],
        ),
    )


def about(request):
    return render(
        request,
        "about.html",
        _base_context(
            active="about",
            page_title="About Marco Baldanza, Luma Tech Solutions, Marlow",
            page_description=(
                "Veteran-owned tech business in Marlow run by Marco Baldanza, "
                "an engineer with a deep infrastructure and software background."
            ),
        ),
    )


def portfolio(request):
    return render(
        request,
        "portfolio.html",
        _base_context(
            active="portfolio",
            page_title="Case Studies — Wi-Fi, CCTV, Smart Home | Luma Tech",
            page_description=(
                "Recent work: a whole-property UniFi network in Maidenhead, "
                "smart-home builds, mobile apps and small-business websites."
            ),
            case_studies=CASE_STUDIES,
        ),
    )


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        # Verify reCAPTCHA before trusting the rest of the form. We do this
        # outside form.is_valid() so a low score short-circuits other work.
        token = request.POST.get("g-recaptcha-response", "")
        remote_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
        passed, score, reason = _verify_recaptcha(token, remote_ip)
        if not passed:
            log.info("reCAPTCHA rejected contact form: score=%.2f reason=%s", score, reason)
            form.add_error(None, "We couldn't verify your submission. Please try again, or email us directly.")
        elif form.is_valid():
            submission = form.save()
            try:
                send_mail(
                    subject=f"[Luma Tech] New enquiry from {submission.name}",
                    message=(
                        f"Name:     {submission.name}\n"
                        f"Email:    {submission.email}\n"
                        f"Phone:    {submission.phone or '—'}\n"
                        f"Audience: {submission.get_audience_display() or '—'}\n"
                        f"Service:  {submission.get_service_display()}\n"
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
        initial = {"source": request.GET.get("source", "")}

        # ?service=support → preselect the "Interested in" dropdown.
        # Validate against SERVICE_CHOICES so a bad URL doesn't drop a missing
        # option into the form.
        service = request.GET.get("service", "").strip().lower()
        valid_services = {key for key, _ in SERVICE_CHOICES}
        if service in valid_services:
            initial["service"] = service

        # ?plan=essential → pre-populate the message with the chosen tier.
        # ?audience=home|business → pre-select the audience on the form and
        # tailor the message wording. Default behaviour (no param) leaves it blank.
        audience = request.GET.get("audience", "").strip().lower()
        if audience in {"home", "business"}:
            initial["audience"] = audience

        # ?plan=essential|professional|concierge → pre-populate the message.
        # Plan names are shared between home and business lists, so a single
        # lookup off either list is enough to find the canonical capitalisation.
        plan = request.GET.get("plan", "").strip().lower()
        plan_lookup = {p["name"].lower(): p["name"] for p in HOME_CARE_PLANS}
        if plan in plan_lookup:
            scope = (
                "for our business" if audience == "business"
                else "for our home" if audience == "home"
                else ""
            )
            initial["message"] = (
                f"I'm interested in the {plan_lookup[plan]} support package"
                f"{' ' + scope if scope else ''}. "
                "Please can you tell me more."
            )

        form = ContactForm(initial=initial)

    return render(
        request,
        "contact.html",
        _base_context(
            active="contact",
            page_title="Contact Luma Tech — Marlow, Maidenhead & Henley Engineer",
            page_description=(
                "Talk to Marco about Wi-Fi, CCTV, smart-home or IT support "
                "across Marlow, Maidenhead, Henley and the Thames Valley."
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
            page_title="Thanks — we'll be in touch | Luma Tech",
            page_description="Your enquiry has been received. We reply within one working day.",
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
            page_title="Notes on Wi-Fi, Smart Home & IT | Luma Tech",
            page_description=(
                "Practical write-ups on networking, security, smart-home "
                "automation and software from a Marlow-based engineer."
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
            page_title=f"{post.title} | Luma Tech",
            page_description=post.seo_description,
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Blog", reverse("blog")),
                (post.get_pillar_display(), reverse("blog")),
                (post.title, post.get_absolute_url()),
            ],
            post=post,
            related=related,
        ),
    )


# --- Areas served ---

def areas_index(request):
    return render(
        request,
        "areas/index.html",
        _base_context(
            active="services",
            page_title="Areas Covered — Marlow, Maidenhead, Henley & Bucks | Luma Tech",
            page_description=(
                "Where we work: Marlow, Maidenhead, Henley-on-Thames, "
                "Beaconsfield, Bourne End, Cookham and High Wycombe."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Areas", reverse("areas")),
            ],
        ),
    )


def area_marlow(request):
    return render(
        request,
        "areas/marlow.html",
        _base_context(
            active="services",
            page_title="Wi-Fi, CCTV & IT Support in Marlow | Luma Tech",
            page_description=(
                "Marlow-based engineer for Wi-Fi installation, CCTV, smart-home "
                "and IT support. Local response, fixed-price proposals."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Areas", reverse("areas")),
                ("Marlow", reverse("area_marlow")),
            ],
            town="Marlow",
        ),
    )


def area_maidenhead(request):
    featured = next(
        (c for c in CASE_STUDIES if c["slug"] == "littlewick-house"),
        None,
    )
    return render(
        request,
        "areas/maidenhead.html",
        _base_context(
            active="services",
            page_title="Wi-Fi, CCTV & IT Support in Maidenhead | Luma Tech",
            page_description=(
                "Whole-property UniFi networks, CCTV and smart-home design "
                "for larger homes in Maidenhead, Bray, Furze Platt and Cox Green."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Areas", reverse("areas")),
                ("Maidenhead", reverse("area_maidenhead")),
            ],
            town="Maidenhead",
            featured_case=featured,
        ),
    )


def terms(request):
    return render(
        request,
        "terms.html",
        _base_context(
            active=None,
            page_title="Terms and Conditions | Luma Tech",
            page_description=(
                "Website terms and conditions for Luma Tech Solutions."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Terms", reverse("terms")),
            ],
        ),
    )


def privacy(request):
    return render(
        request,
        "privacy.html",
        _base_context(
            active=None,
            page_title="Privacy Policy | Luma Tech",
            page_description=(
                "How Luma Tech Solutions collects, uses and protects your "
                "personal data — UK GDPR-compliant."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Privacy", reverse("privacy")),
            ],
        ),
    )


def area_henley(request):
    return render(
        request,
        "areas/henley.html",
        _base_context(
            active="services",
            page_title="Wi-Fi, CCTV & IT Support in Henley-on-Thames | Luma Tech",
            page_description=(
                "Wi-Fi, CCTV and smart-home design for period homes and "
                "riverside properties in Henley-on-Thames, Remenham, "
                "Hambleden and Mill End."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Areas", reverse("areas")),
                ("Henley-on-Thames", reverse("area_henley")),
            ],
            town="Henley-on-Thames",
        ),
    )


def healthz(request):
    return HttpResponse("ok\n", content_type="text/plain")
