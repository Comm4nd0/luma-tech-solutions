import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ContactForm, JobApplicationForm, QuoteRequestForm
from .models import (
    BlogPost,
    BUDGET_CHOICES,
    JOB_ROLE_CHOICES,
    PROPERTY_TYPE_CHOICES,
    QUOTE_SERVICE_CHOICES,
    SERVICE_CHOICES,
    TIMELINE_CHOICES,
)

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
        "title": "Physical Security",
        "tagline": "CCTV, access control, alarms and smart locks — professionally installed and integrated with your network.",
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


HERO_SLIDES = [
    {
        "key": "intro",
        "eyebrow": "Marlow · Maidenhead · the Thames Valley",
        "headline_top": "Wi-Fi that actually",
        "headline_bottom": "reaches every room.",
        "lede": (
            "If your home or office is too big for consumer routers — and the "
            "mesh kit didn't fix it — we engineer efficient business-grade "
            "networks for larger homes and small businesses that need it to "
            "just work. Plus security, automation, development and support. "
            "Based in Marlow, covering the Thames Valley."
        ),
        "primary_cta_text": "Get a quote",
        "primary_cta_url_name": "quote",
        "primary_cta_source": "home-wifi-hero",
        "secondary_cta_text": "Explore services",
        "secondary_cta_url_name": "services",
        "illustration": "hero",
    },
    {
        "key": "networking",
        "eyebrow": "Wi-Fi & Networking",
        "headline_top": "Built like office kit.",
        "headline_bottom": "Sized for homes.",
        "lede": (
            "UniFi networks — surveyed, cabled and documented. PoE access "
            "points placed from a real site survey, managed switches and "
            "VLANs underneath. No mesh, no guesswork."
        ),
        "primary_cta_text": "Get a Wi-Fi quote",
        "primary_cta_url_name": "quote",
        "primary_cta_source": "home-networking-hero",
        "secondary_cta_text": "See LittleWick House",
        "secondary_cta_url_name": "portfolio",
        "illustration": "networking",
    },
    {
        "key": "security",
        "eyebrow": "Physical Security",
        "headline_top": "CCTV, access and alarms —",
        "headline_bottom": "one integrated system.",
        "lede": (
            "CCTV, access control, alarms and smart locks — professionally "
            "installed and integrated with the same network we built. "
            "Recorded on-site, not on someone else's cloud."
        ),
        "primary_cta_text": "Get a CCTV quote",
        "primary_cta_url_name": "quote",
        "primary_cta_source": "home-security-hero",
        "secondary_cta_text": "How we do security",
        "secondary_cta_url_name": "service_security",
        "illustration": "security",
    },
    {
        "key": "development",
        "eyebrow": "App & Web Development",
        "headline_top": "Apps and websites,",
        "headline_bottom": "built and supported.",
        "lede": (
            "Custom websites, web apps and mobile apps — designed, shipped "
            "and looked after by the same engineer. No agency hand-offs, "
            "no offshore black-box."
        ),
        "primary_cta_text": "Scope a build",
        "primary_cta_url_name": "quote",
        "primary_cta_source": "home-development-hero",
        "secondary_cta_text": "Recent work",
        "secondary_cta_url_name": "portfolio",
        "illustration": "development",
    },
    {
        "key": "automation",
        "eyebrow": "Home Automation",
        "headline_top": "Smart homes that stay",
        "headline_bottom": "smart offline.",
        "lede": (
            "Local-first Home Assistant setups for lighting, climate, scenes "
            "and access. Private, fast, and still working when your "
            "broadband isn't."
        ),
        "primary_cta_text": "Plan my smart home",
        "primary_cta_url_name": "quote",
        "primary_cta_source": "home-automation-hero",
        "secondary_cta_text": "See a real install",
        "secondary_cta_url_name": "portfolio",
        "illustration": "automation",
    },
    {
        "key": "support",
        "eyebrow": "Support & Care Plans",
        "headline_top": "Care plans from £75.",
        "headline_bottom": "One engineer, every call.",
        "lede": (
            "Monitoring, response SLAs and the same person on the phone "
            "every time. So your home or office tech keeps working long "
            "after the install is finished."
        ),
        "primary_cta_text": "Talk to support",
        "primary_cta_url_name": "contact",
        "primary_cta_source": "home-support-hero",
        "secondary_cta_text": "How support works",
        "secondary_cta_url_name": "service_support",
        "illustration": "support",
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


# --- FAQ data ---
# Shown on the home page and (subset) on service pages. Also rendered into
# FAQPage JSON-LD so Google can show them as rich results / featured snippets.
# Keep answers short, plain-English, keyword-rich without keyword stuffing.

FAQS_GENERAL = [
    {
        "q": "What areas do you cover?",
        "a": (
            "We're based in Marlow and cover the Thames Valley — Marlow, "
            "Maidenhead, Henley-on-Thames, Beaconsfield, Bourne End, "
            "Cookham and High Wycombe. We'll travel further across "
            "Buckinghamshire and Berkshire by arrangement."
        ),
    },
    {
        "q": "How much does a Wi-Fi installation cost?",
        "a": (
            "Every property is different — the honest answer is we'll quote "
            "after a site survey. A typical large-home UniFi install (4–6 "
            "access points, switching, cabling) runs from around £3,000; "
            "bigger properties with 8+ APs, multiple VLANs and CCTV usually "
            "fall between £8,000 and £20,000. Every quote is fixed-price and "
            "written down — no day rates, no surprise add-ons."
        ),
    },
    {
        "q": "How long does an installation take?",
        "a": (
            "A standard home Wi-Fi install is usually 1–2 days on site once "
            "we've finished the survey and ordered kit. Whole-property "
            "networks with structured cabling can run to 5–10 days, often "
            "split across visits so we work around your routine. We agree "
            "the schedule up-front and stick to it."
        ),
    },
    {
        "q": "Do I have to sign up to a care plan?",
        "a": (
            "No. Every install comes with 30 days of post-install support "
            "as standard. Care plans are optional from there — they're for "
            "clients who want monitoring, faster response, and one engineer "
            "who knows the system on call. From £75/month + VAT for homes "
            "or £25/user/month for small businesses."
        ),
    },
    {
        "q": "Why UniFi instead of consumer mesh kit?",
        "a": (
            "Consumer mesh and powerline kit are designed for small flats "
            "with thin walls. Once you add a second storey, thick masonry, "
            "or 200+ m² of floorspace, the physics catch up. UniFi gives "
            "you wired access points (no halving bandwidth every hop), "
            "real diagnostics, and one dashboard for Wi-Fi, switching and "
            "CCTV — the same kit that runs in offices and hotels."
        ),
    },
    {
        "q": "Will my CCTV footage be stored in the cloud?",
        "a": (
            "Not unless you specifically want it to be. We default to "
            "UniFi Protect, which records to a small NVR at your house. "
            "No monthly subscription, no third-party AI looking through "
            "your footage, and it keeps working when your broadband doesn't."
        ),
    },
]


# Networking-specific FAQs, used on the Wi-Fi service page.
FAQS_NETWORKING = [
    {
        "q": "Will UniFi work in my period property?",
        "a": (
            "Yes — and we design specifically for older houses. Lath-and-"
            "plaster walls, foil-backed insulation and thick masonry "
            "absorb Wi-Fi, so the answer is more access points placed "
            "correctly, fed by wired Cat6 — not a bigger mesh kit. We've "
            "done Georgian, Victorian and listed properties around Marlow "
            "and Henley."
        ),
    },
    {
        "q": "Do I need to run cables everywhere?",
        "a": (
            "We run Cat6 from a central comms cupboard to each access "
            "point and camera. Where the loft is accessible we drop down "
            "the walls; where it isn't, we use existing voids, conduits, "
            "or surface-mount trunking discreetly. We plan all the runs "
            "in the site survey so you see exactly what's going where "
            "before we drill anything."
        ),
    },
    {
        "q": "Can you cover the garden and outbuildings?",
        "a": (
            "Yes. Outdoor APs, point-to-point links to garden offices and "
            "annexes, and weatherproof CCTV coverage are part of what we "
            "design. We've done pool houses, stable blocks, garden offices "
            "and large gardens across the Thames Valley."
        ),
    },
]


# Security-specific FAQs, used on the Physical Security service page.
FAQS_SECURITY = [
    {
        "q": "Is the CCTV recorded in the cloud?",
        "a": (
            "Not by default. UniFi Protect records to an NVR at your "
            "property, so footage stays with you. No monthly subscription "
            "and no third-party AI rifling through your footage. We can "
            "add encrypted off-site backup as an option if you want it."
        ),
    },
    {
        "q": "Do the cameras work in the dark?",
        "a": (
            "Yes. The cameras we install have proper infrared night vision "
            "and (on most models) low-light colour modes. On-device AI "
            "tells person from vehicle from package, so your phone only "
            "buzzes for things that matter."
        ),
    },
    {
        "q": "Can I view it on my phone?",
        "a": (
            "Yes — secure remote viewing through the UniFi Protect app on "
            "iOS and Android. Two-factor authentication, end-to-end "
            "encrypted, and no public ports opened on your router."
        ),
    },
]


JOB_ROLES = [
    {
        "key": "network",
        "title": "UniFi Network Engineer",
        "summary": "Design and deploy UniFi networks for homes and small businesses across the Thames Valley.",
        "responsibilities": [
            "Plan and install UniFi Wi-Fi, switching and gateway kit on residential and small-business sites",
            "Configure VLANs, firewall rules, guest networks and Protect CCTV — properly segmented, properly documented",
            "Commission, label and hand-over networks with clean as-built documentation",
            "Triage and resolve client issues remotely (UniFi Site Manager) and on-site",
        ],
        "ideal": [
            "Hands-on UniFi experience — Dream Machines, switches, APs, Protect",
            "Comfortable reading floor plans and planning AP placement for coverage",
            "Working knowledge of VLANs, DHCP, DNS and basic firewall rules",
            "Tidy worker — cable management is a craft, not an afterthought",
        ],
        "logistics": "Based in Marlow / Maidenhead. Driving licence and own transport essential. Mix of on-site and remote work.",
    },
    {
        "key": "infrastructure",
        "title": "Infrastructure Engineer — Cable Installations",
        "summary": "First-fix and second-fix structured cabling for residential and small-commercial UniFi installations.",
        "responsibilities": [
            "Pull and terminate Cat6/Cat6a runs through lofts, voids, conduit and trunking",
            "Install and patch keystones, faceplates and patch panels — labelled and tested",
            "Mount APs, CCTV cameras, switches and small comms cabinets",
            "Work alongside the network engineer to turn a design into a clean, working install",
        ],
        "ideal": [
            "Proven structured-cabling experience (Cat5e/Cat6/Cat6a) and confident with a Fluke or similar tester",
            "Good with power tools, ladders and access equipment — H&S aware",
            "ECS / CSCS / IPAF tickets a bonus, not essential",
            "Pride in finished work and a willingness to do it right the first time",
        ],
        "logistics": "Field-based across Marlow, Maidenhead, Henley and the Thames Valley. Driving licence and own transport essential.",
    },
    {
        "key": "cyber",
        "title": "Cyber Security Engineer",
        "summary": "Harden the networks we build and help small-business clients reach Cyber Essentials and beyond.",
        "responsibilities": [
            "Design and review firewall, VLAN and remote-access policies on UniFi gateways and cloud services",
            "Run vulnerability scans, patch reviews and config audits for client networks and endpoints",
            "Support clients through Cyber Essentials and Cyber Essentials Plus certification",
            "Investigate and triage incidents — phishing, account compromise, suspicious traffic — and lead the response",
            "Tighten Microsoft 365 / Google Workspace tenants: MFA, conditional access, mailbox rules, retention",
        ],
        "ideal": [
            "Solid grounding in network security fundamentals (firewalls, segmentation, IDS/IPS, VPNs)",
            "Hands-on with at least one EDR / endpoint suite and one cloud-identity platform (Entra ID, Google Workspace)",
            "Comfortable explaining risk in plain English to non-technical business owners",
            "Relevant cert (CompTIA Security+, BTL1, SC-200, OSCP) helpful but practical experience matters more",
            "DBS-friendly — some clients require it",
        ],
        "logistics": "Hybrid — mostly remote with site visits across Marlow, Maidenhead, Henley and the Thames Valley. Driving licence preferred.",
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
            page_title="Wi-Fi Installation Marlow, CCTV & IT Support | Luma Tech",
            page_description=(
                "Marlow-based engineer for proper UniFi Wi-Fi, CCTV and "
                "smart-home installation across Marlow, Maidenhead, Henley "
                "and the Thames Valley. Fixed-price quotes, no mesh."
            ),
            testimonials=TESTIMONIALS,
            featured_case=featured,
            hero_slides=HERO_SLIDES,
            faqs=FAQS_GENERAL,
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
                "Wi-Fi design, CCTV installation, app development, smart-home "
                "automation and IT support for homes and small businesses "
                "across Marlow, Maidenhead, Henley and the Thames Valley."
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
            page_title="UniFi Wi-Fi Installation, Marlow & Henley | Luma Tech",
            page_description=(
                "Professionally engineered UniFi Wi-Fi for large and period "
                "homes — Marlow, Maidenhead, Henley-on-Thames and the Thames "
                "Valley. Wired access points, fixed-price quotes, no mesh."
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
            faqs=FAQS_NETWORKING,
        ),
    )


def service_security(request):
    return render(
        request,
        "services/security.html",
        _base_context(
            active="security",
            page_title="CCTV Installation Marlow, Maidenhead & Henley | Luma Tech",
            page_description=(
                "UniFi Protect CCTV, access control and alarms across Marlow, "
                "Maidenhead, Henley-on-Thames and the Thames Valley. Footage "
                "stays on your kit — no cloud subscription required."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("Physical Security", reverse("service_security")),
            ],
            service_name="Physical Security",
            service_type="CCTV Installation",
            service_url=reverse("service_security"),
            service_description=(
                "UniFi Protect CCTV, access control, alarms, smart locks and "
                "network hardening for homes and businesses across Marlow, "
                "Maidenhead, Beaconsfield and the Thames Valley."
            ),
            faqs=FAQS_SECURITY,
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
            page_title="Smart Home Installer — Marlow, Henley, Maidenhead | Luma Tech",
            page_description=(
                "Local-first Home Assistant smart-home installation. Lighting, "
                "climate, scenes and security across Marlow, Henley-on-Thames, "
                "Maidenhead and the Thames Valley. No cloud lock-in."
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


@require_http_methods(["GET", "POST"])
def careers(request):
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        token = request.POST.get("g-recaptcha-response", "")
        remote_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")
        passed, score, reason = _verify_recaptcha(token, remote_ip)
        if not passed:
            log.info("reCAPTCHA rejected careers form: score=%.2f reason=%s", score, reason)
            form.add_error(
                None,
                "We couldn't verify your submission. Please try again, or email us directly.",
            )
        elif form.is_valid():
            cv = form.cleaned_data["cv"]
            application = form.save(commit=False)
            application.cv_filename = cv.name[:255]
            application.cv_size_bytes = cv.size
            application.save()
            try:
                msg = EmailMessage(
                    subject=f"[Luma Tech] Job application — {application.get_role_display()} — {application.name}",
                    body=(
                        f"Role:    {application.get_role_display()}\n"
                        f"Name:    {application.name}\n"
                        f"Email:   {application.email}\n"
                        f"Phone:   {application.phone or '—'}\n"
                        f"\n"
                        f"Cover note:\n{application.cover_note or '—'}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CAREERS_FORM_RECIPIENT],
                    reply_to=[application.email],
                )
                # Derive MIME type from the validated extension, not the
                # browser-supplied content_type which is user-controlled.
                _CV_MIME = {
                    ".pdf": "application/pdf",
                    ".doc": "application/msword",
                    ".docx": "application/vnd.openxmlformats-officedocument"
                            ".wordprocessingml.document",
                }
                ext = ("." + cv.name.rsplit(".", 1)[-1].lower()
                       if "." in cv.name else "")
                mime = _CV_MIME.get(ext, "application/octet-stream")
                msg.attach(cv.name, cv.read(), mime)
                msg.send(fail_silently=False)
                application.notified = True
                application.save(update_fields=["notified"])
            except Exception:
                log.exception("Failed to send job application notification email")
            messages.success(request, "Thanks — we've received your application.")
            return redirect(reverse("careers_thanks"))
    else:
        initial = {}
        # ?role=network|infrastructure → preselect the role.
        role = request.GET.get("role", "").strip().lower()
        valid_roles = {key for key, _ in JOB_ROLE_CHOICES}
        if role in valid_roles:
            initial["role"] = role
        form = JobApplicationForm(initial=initial)

    return render(
        request,
        "careers.html",
        _base_context(
            active="careers",
            page_title="Careers — Network & Infrastructure Engineers | Luma Tech",
            page_description=(
                "We're hiring a UniFi Network Engineer and an Infrastructure "
                "Engineer (cable installations) to join Luma Tech in Marlow."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Careers", reverse("careers")),
            ],
            roles=JOB_ROLES,
            form=form,
        ),
    )


def careers_thanks(request):
    return render(
        request,
        "careers_thanks.html",
        _base_context(
            active="careers",
            page_title="Application received — thanks | Luma Tech",
            page_description="Your job application has been received. We'll be in touch shortly.",
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
            page_title="Wi-Fi, CCTV & Smart Home Installation in Henley-on-Thames | Luma Tech",
            page_description=(
                "UniFi Wi-Fi, CCTV and smart-home installation for period "
                "homes and riverside properties in Henley-on-Thames, "
                "Remenham, Hambleden and Mill End. Local Marlow engineer."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Areas", reverse("areas")),
                ("Henley-on-Thames", reverse("area_henley")),
            ],
            town="Henley-on-Thames",
        ),
    )


def area_beaconsfield(request):
    return render(
        request,
        "areas/beaconsfield.html",
        _base_context(
            active="services",
            page_title="Wi-Fi, CCTV & Smart Home Installation in Beaconsfield | Luma Tech",
            page_description=(
                "UniFi Wi-Fi, CCTV and smart-home installation for the larger "
                "homes and businesses around Beaconsfield, Knotty Green and "
                "Holtspur. Local Marlow engineer, fixed-price quotes."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Areas", reverse("areas")),
                ("Beaconsfield", reverse("area_beaconsfield")),
            ],
            town="Beaconsfield",
        ),
    )


# --- Quote request ---

@require_http_methods(["GET", "POST"])
def quote(request):
    """Structured quote-request landing page. Captures property type,
    postcode, services, timeline and budget — more qualifying data than the
    generic contact form so we can reply with a real survey slot.
    """
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        token = request.POST.get("g-recaptcha-response", "")
        remote_ip = (
            request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
            or request.META.get("REMOTE_ADDR", "")
        )
        passed, score, reason = _verify_recaptcha(token, remote_ip)
        if not passed:
            log.info(
                "reCAPTCHA rejected quote form: score=%.2f reason=%s",
                score,
                reason,
            )
            form.add_error(
                None,
                "We couldn't verify your submission. Please try again, or email us directly.",
            )
        elif form.is_valid():
            quote_req = form.save()
            try:
                send_mail(
                    subject=f"[Luma Tech] Quote request from {quote_req.name} ({quote_req.postcode})",
                    message=(
                        f"Name:      {quote_req.name}\n"
                        f"Email:     {quote_req.email}\n"
                        f"Phone:     {quote_req.phone or '—'}\n"
                        f"Postcode:  {quote_req.postcode}\n"
                        f"Property:  {quote_req.get_property_type_display()}\n"
                        f"Services:  {quote_req.services_display() or '—'}\n"
                        f"Timeline:  {quote_req.get_timeline_display() or '—'}\n"
                        f"Source:    {quote_req.source or '—'}\n"
                        f"\n"
                        f"Notes:\n{quote_req.notes or '—'}\n"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_FORM_RECIPIENT],
                    fail_silently=False,
                )
                quote_req.notified = True
                quote_req.save(update_fields=["notified"])
            except Exception:
                log.exception("Failed to send quote notification email")
            messages.success(request, "Thanks — we'll be in touch shortly.")
            return redirect(reverse("quote_thanks"))
    else:
        initial = {"source": request.GET.get("source", "")}

        # ?service=networking → preselect that service in the multi-select.
        # Accept multiple comma-separated keys: ?service=networking,security
        service_param = request.GET.get("service", "").strip().lower()
        if service_param:
            valid_keys = {k for k, _ in QUOTE_SERVICE_CHOICES}
            selected = [
                s for s in service_param.split(",") if s.strip() in valid_keys
            ]
            if selected:
                initial["services"] = selected

        # ?property=home_large → preselect the property type.
        prop = request.GET.get("property", "").strip().lower()
        valid_props = {k for k, _ in PROPERTY_TYPE_CHOICES}
        if prop in valid_props:
            initial["property_type"] = prop

        form = QuoteRequestForm(initial=initial)

    return render(
        request,
        "quote.html",
        _base_context(
            active="quote",
            page_title="Get a Quote — Wi-Fi, CCTV & Smart Home | Luma Tech",
            page_description=(
                "Tell us about your property and we'll come back with a "
                "fixed-price quote. Marlow-based engineer, covering the "
                "Thames Valley. Most surveys booked within the week."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Get a quote", reverse("quote")),
            ],
            form=form,
            property_type_choices=PROPERTY_TYPE_CHOICES,
            timeline_choices=TIMELINE_CHOICES,
            service_choices=QUOTE_SERVICE_CHOICES,
        ),
    )


def quote_thanks(request):
    return render(
        request,
        "quote_thanks.html",
        _base_context(
            active="quote",
            page_title="Quote request received — thanks | Luma Tech",
            page_description=(
                "Your quote request has been received. We'll be in touch "
                "within one working day to book your free site survey."
            ),
        ),
    )


def healthz(request):
    return HttpResponse("ok\n", content_type="text/plain")
