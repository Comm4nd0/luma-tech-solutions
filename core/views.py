import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .content import (
    BUSINESS_CARE_PLANS,
    CASE_STUDIES,
    FAQS_AI_CAMERAS,
    FAQS_CONSTRUCTION,
    FAQS_GENERAL,
    FAQS_NETWORKING,
    FAQS_SECURITY,
    HOME_CARE_PLANS,
    JOB_ROLES,
    PILLARS,
    TESTIMONIALS,
    WEBSITE_DEMOS,
)
from .forms import ContactForm, JobApplicationForm, QuoteRequestForm
from .models import (
    AUDIENCE_CHOICES,
    BlogPost,
    JOB_ROLE_CHOICES,
    PROPERTY_TYPE_CHOICES,
    QUOTE_SERVICE_CHOICES,
    SERVICE_CHOICES,
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


def _client_ip(request):
    """Best-effort client IP, trusting the proxy's first X-Forwarded-For hop."""
    return (
        request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        or request.META.get("REMOTE_ADDR", "")
    )


def _passes_recaptcha(request, form, *, label):
    """Verify reCAPTCHA for a POSTed form. On failure, attach a generic
    non-field error to ``form`` and return False. Run before form.is_valid()
    so a low score short-circuits the rest of the work.
    """
    token = request.POST.get("g-recaptcha-response", "")
    passed, score, reason = _verify_recaptcha(token, _client_ip(request))
    if not passed:
        log.info(
            "reCAPTCHA rejected %s form: score=%.2f reason=%s", label, score, reason
        )
        form.add_error(
            None,
            "We couldn't verify your submission. Please try again, or email "
            "us directly.",
        )
    return passed


# MIME type per validated CV extension — derived from the allowlisted
# extension, never the browser-supplied content_type (which is user-controlled).
_CV_MIME = {
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def _notify(subject, body, *, recipient=None, reply_to=None, attachments=None):
    """Send a plain-text notification email. Returns True on success, False on
    failure (which is logged). Never raises: a delivery failure must not 500
    the visitor's submission — the row is already saved and shows notified=False.
    """
    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient or settings.CONTACT_FORM_RECIPIENT],
        reply_to=reply_to,
    )
    for fname, content, mime in attachments or []:
        msg.attach(fname, content, mime)
    try:
        msg.send(fail_silently=False)
        return True
    except Exception:
        log.exception("Failed to send notification email: %s", subject)
        return False


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
                "Marlow-based engineer for business-grade UniFi Wi-Fi, CCTV and "
                "smart-home installation across Marlow, Maidenhead, Henley "
                "and the Thames Valley. Fixed-price quotes, no mesh."
            ),
            testimonials=TESTIMONIALS,
            featured_case=featured,
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
                "UniFi Protect CCTV, access control, alarms and "
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


def service_ai_cameras(request):
    return render(
        request,
        "services/ai_cameras.html",
        _base_context(
            active="services",
            page_title="AI Camera Systems — ANPR, Smart CCTV, Privacy-First | Luma Tech",
            page_description=(
                "AI cameras done right across Marlow, Maidenhead, "
                "Henley and the Thames Valley. ANPR for construction "
                "sites, smart home & family monitoring, scheduled and "
                "geofenced recording. Footage stays on your kit."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Services", reverse("services")),
                ("AI Camera Systems", reverse("service_ai_cameras")),
            ],
            service_name="AI Camera Systems",
            service_type="CCTV Installation",
            service_url=reverse("service_ai_cameras"),
            service_description=(
                "AI camera systems with on-device person, vehicle, package, "
                "animal and number-plate recognition. Designed for "
                "construction sites, homes and small businesses across "
                "Marlow, Maidenhead, Henley and the Thames Valley. "
                "Scheduled recording, geofenced arming, on-site storage — "
                "no third-party cloud."
            ),
            faqs=FAQS_AI_CAMERAS,
        ),
    )


def construction(request):
    """Landing page for builders, developers and site managers — site
    security/ANPR for the duration of a build, new-build pre-wire packages,
    and the trade-partner offer. Deliberately speaks procurement language
    (per-plot pricing, RAMS, programme) rather than homeowner language.
    """
    chiltern_yard = next(
        (c for c in CASE_STUDIES if c["slug"] == "chiltern-yard-anpr"), None
    )
    return render(
        request,
        "construction.html",
        _base_context(
            active="construction",
            page_title="Construction Site Security, ANPR & New-Build Pre-Wire | Luma Tech",
            page_description=(
                "Site CCTV and ANPR for the duration of your build, plus "
                "new-build pre-wire packages priced per plot. Builders and "
                "developers across Marlow, Maidenhead, Henley and the "
                "Thames Valley. DPIA and signage handled."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Builders & construction", reverse("construction")),
            ],
            service_name="Construction Site Security & Pre-Wire",
            service_type="Security System Installation",
            service_url=reverse("construction"),
            service_description=(
                "Construction site CCTV, gate ANPR and new-build structured "
                "cabling pre-wire for builders and developers across Marlow, "
                "Maidenhead, Henley and the Thames Valley. Fixed monthly "
                "site-security pricing, per-plot pre-wire packages, DPIA "
                "and signage included."
            ),
            faqs=FAQS_CONSTRUCTION,
            featured_case=chiltern_yard,
            whatsapp_prefill=(
                "Hi, I'm a builder/site manager — I'd like to talk about "
                "site security or pre-wire for a project."
            ),
        ),
    )


def capability_statement(request):
    """Print-friendly one-page capability statement — the thing a site
    manager forwards to a director. Standalone template (no site chrome)
    so it prints/saves to PDF cleanly from the browser.
    """
    return render(
        request,
        "capability_statement.html",
        {
            "page_title": "Capability Statement — Luma Tech Solutions",
        },
    )


def case_study(request, slug):
    case = next((c for c in CASE_STUDIES if c["slug"] == slug), None)
    if case is None:
        raise Http404("Unknown case study")
    related = [c for c in CASE_STUDIES if c["slug"] != slug][:3]
    return render(
        request,
        "portfolio/case_detail.html",
        _base_context(
            active="portfolio",
            page_title=f"Case Study: {case['title']} | Luma Tech",
            page_description=(case["summary"][:157] + "…")
            if len(case["summary"]) > 160
            else case["summary"],
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Portfolio", reverse("portfolio")),
                (case["title"], reverse("case_study", args=[slug])),
            ],
            case=case,
            related=related,
        ),
    )


def camera_privacy(request):
    return render(
        request,
        "camera_privacy.html",
        _base_context(
            active="services",
            page_title="Our Approach to Camera Privacy | Luma Tech",
            page_description=(
                "How Luma Tech installs CCTV and AI cameras: on-site "
                "recording, on-device AI, scheduled & geofenced arming, "
                "privacy masks, per-user 2FA access, DPIA and signage. "
                "The full write-up — useful before you commission us, "
                "and as a DPIA artefact."
            ),
            breadcrumbs=[
                ("Home", reverse("home")),
                ("Our approach to camera privacy", reverse("camera_privacy")),
            ],
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
            website_demos=WEBSITE_DEMOS,
        ),
    )


def showcase_demo(request, slug):
    """Render a standalone one-page demo customer website.

    Deliberately does NOT use _base_context() — these pages have their own
    self-contained design and no Luma chrome.
    """
    demo = next((d for d in WEBSITE_DEMOS if d["slug"] == slug), None)
    if demo is None:
        raise Http404("Unknown demo")
    return render(request, demo["template"], {"demo": demo})


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if _passes_recaptcha(request, form, label="contact") and form.is_valid():
            submission = form.save()
            sent = _notify(
                subject=f"[Luma Tech] New enquiry from {submission.name}",
                body=(
                    f"Name:     {submission.name}\n"
                    f"Email:    {submission.email}\n"
                    f"Phone:    {submission.phone or '—'}\n"
                    f"Audience: {submission.get_audience_display() or '—'}\n"
                    f"Service:  {submission.get_service_display()}\n"
                    f"\n"
                    f"{submission.message}\n"
                ),
                reply_to=[submission.email],
            )
            if sent:
                submission.notified = True
                submission.save(update_fields=["notified"])
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
        # ?audience=home|business|trade → pre-select the audience on the form
        # and tailor the message wording. Default behaviour (no param) leaves
        # it blank.
        audience = request.GET.get("audience", "").strip().lower()
        if audience in {key for key, _ in AUDIENCE_CHOICES}:
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
        if _passes_recaptcha(request, form, label="careers") and form.is_valid():
            cv = form.cleaned_data["cv"]
            application = form.save(commit=False)
            application.cv_filename = cv.name[:255]
            application.cv_size_bytes = cv.size
            # Persist the CV to the data volume so a failed notification email
            # doesn't lose the application — it stays recoverable from admin.
            cv.seek(0)
            application.cv_file = cv
            application.save()

            ext = "." + cv.name.rsplit(".", 1)[-1].lower() if "." in cv.name else ""
            mime = _CV_MIME.get(ext, "application/octet-stream")
            # Attach from the stored copy so the email matches what we kept.
            application.cv_file.open("rb")
            try:
                cv_bytes = application.cv_file.read()
            finally:
                application.cv_file.close()

            sent = _notify(
                subject=(
                    f"[Luma Tech] Job application — "
                    f"{application.get_role_display()} — {application.name}"
                ),
                body=(
                    f"Role:    {application.get_role_display()}\n"
                    f"Name:    {application.name}\n"
                    f"Email:   {application.email}\n"
                    f"Phone:   {application.phone or '—'}\n"
                    f"\n"
                    f"Cover note:\n{application.cover_note or '—'}\n"
                ),
                recipient=settings.CAREERS_FORM_RECIPIENT,
                reply_to=[application.email],
                attachments=[(application.cv_filename, cv_bytes, mime)],
            )
            if sent:
                application.notified = True
                application.save(update_fields=["notified"])
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
        if _passes_recaptcha(request, form, label="quote") and form.is_valid():
            quote_req = form.save()
            sent = _notify(
                subject=(
                    f"[Luma Tech] Quote request from {quote_req.name} "
                    f"({quote_req.postcode})"
                ),
                body=(
                    f"Name:      {quote_req.name}\n"
                    f"Email:     {quote_req.email}\n"
                    f"Phone:     {quote_req.phone or '—'}\n"
                    f"Postcode:  {quote_req.postcode}\n"
                    f"Property:  {quote_req.get_property_type_display()}\n"
                    f"Services:  {quote_req.services_display() or '—'}\n"
                    f"Timeline:  {quote_req.get_timeline_display() or '—'}\n"
                    f"Budget:    {quote_req.get_budget_display() or '—'}\n"
                    f"Source:    {quote_req.source or '—'}\n"
                    f"\n"
                    f"Notes:\n{quote_req.notes or '—'}\n"
                ),
                reply_to=[quote_req.email],
            )
            if sent:
                quote_req.notified = True
                quote_req.save(update_fields=["notified"])
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
