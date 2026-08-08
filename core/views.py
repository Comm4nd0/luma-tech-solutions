import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .content import (
    AREA_FAQS,
    AREA_PAGES,
    BLOG_PILLAR_SERVICES,
    CARE_TIERS,
    CASE_STUDIES,
    FAQS_AI_CAMERAS,
    FAQS_CONSTRUCTION,
    FAQS_GENERAL,
    FAQS_NETWORKING,
    FAQS_SECURITY,
    JOB_ROLES,
    PILLARS,
    SERVICE_PAGES,
    TESTIMONIALS,
    THANKS_PAGES,
    WEBSITE_DEMOS,
    care_plans,
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


# Submissions allowed per IP per window, per worker process.
RATE_LIMIT_MAX = 5
RATE_LIMIT_WINDOW = 600  # seconds


def _rate_limited(request, form, *, bucket):
    """Throttle repeat submissions from one IP.

    Deliberately modest in what it claims: the cache is per-process, so with
    three gunicorn workers the effective ceiling is 3x RATE_LIMIT_MAX, and it
    resets on deploy. This is spam friction, not a security control —
    reCAPTCHA and the honeypot are the controls. Storing the IP on the model
    instead would be a new category of personal data and would need the
    privacy page updating, so it stays in the cache.
    """
    ip = _client_ip(request)
    if not ip:
        return False
    key = "ratelimit:%s:%s" % (bucket, ip)
    count = cache.get(key, 0)
    if count >= RATE_LIMIT_MAX:
        log.info("Rate-limited %s submission from %s", bucket, ip)
        form.add_error(
            None,
            "That's a few submissions in a short space of time. Please wait a "
            "few minutes and try again, or email us directly.",
        )
        return True
    # add() only sets when absent, so the window starts at the first hit and
    # doesn't slide forward with every subsequent one.
    if not cache.add(key, 1, RATE_LIMIT_WINDOW):
        try:
            cache.incr(key)
        except ValueError:
            cache.add(key, 1, RATE_LIMIT_WINDOW)
    return False


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


def _crumbs(*trail):
    """Breadcrumbs from (label, url_name) pairs, reversed at request time."""
    return [(label, reverse(url_name)) for label, url_name in trail]


def _related_services(pillar):
    """Service pages a post in this pillar should link to."""
    keys = BLOG_PILLAR_SERVICES.get(pillar) or BLOG_PILLAR_SERVICES["general"]
    return [
        {
            "title": SERVICE_PAGES[k]["service_name"],
            "blurb": SERVICE_PAGES[k]["service_description"],
            "url": reverse(SERVICE_PAGES[k]["url_name"]),
        }
        for k in keys
    ]


def _area_links():
    """The four town pages, for the 'where we work' line on article pages."""
    return [
        {"label": page["town"], "url": reverse(page["url_name"])}
        for page in AREA_PAGES.values()
    ]


def _featured_case(slug=None):
    """The flagged case study, or a specific one by slug."""
    if slug is None:
        return next((c for c in CASE_STUDIES if c["featured"]), CASE_STUDIES[0])
    return next((c for c in CASE_STUDIES if c["slug"] == slug), None)


def _render_service_page(request, key, **extra):
    """Render one of the SERVICE_PAGES entries.

    ``faqs`` is only added when the page actually defines it — defaulting it
    would give three service pages a FAQ section and a FAQPage JSON-LD block
    they have never had.
    """
    page = SERVICE_PAGES[key]
    ctx = _base_context(
        active=page["active"],
        page_title=page["page_title"],
        page_description=page["page_description"],
        breadcrumbs=_crumbs(
            ("Home", "home"),
            ("Services", "services"),
            (page["crumb"], page["url_name"]),
        ),
        service_name=page["service_name"],
        service_type=page["service_type"],
        # A path, not the URL name: _service_schema.html renders
        # "{{ SITE_URL }}{{ service_url }}" straight into JSON-LD.
        service_url=reverse(page["url_name"]),
        service_description=page["service_description"],
        **extra,
    )
    if page.get("faqs"):
        ctx["faqs"] = page["faqs"]
    return render(request, page["template"], ctx)


def _render_area_page(request, key):
    """Render one of the AREA_PAGES entries."""
    page = AREA_PAGES[key]
    ctx = _base_context(
        active="services",
        page_title=page["page_title"],
        page_description=page["page_description"],
        breadcrumbs=_crumbs(
            ("Home", "home"),
            ("Areas", "areas"),
            (page["town"], page["url_name"]),
        ),
        town=page["town"],
        area_url=reverse(page["url_name"]),
        area_source=page["source"],
        area_quote_label=page["quote_label"],
        area_engineer_note=page["engineer_note"],
        area_survey_note=page["survey_note"],
        area_included=page["included"],
        area_also_serving=page["also_serving"],
        area_also_serving_tail=page["also_serving_tail"],
        area_schema_name=page["schema_name"],
        area_schema_description=page["schema_description"],
        faqs=AREA_FAQS[key],
        faq_title=f"{page['town']} — common questions.",
        faq_eyebrow=f"Asked in {page['town']}",
    )
    if "featured_case_slug" in page:
        ctx["featured_case"] = _featured_case(page["featured_case_slug"])
    return render(request, page["template"], ctx)


def _render_thanks_page(request, key):
    """Render one of the THANKS_PAGES entries."""
    page = THANKS_PAGES[key]
    return render(
        request,
        page["template"],
        _base_context(
            active=page["active"],
            page_title=page["page_title"],
            page_description=page["page_description"],
        ),
    )


def home(request):
    featured = _featured_case()
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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Services", "services"),
            ),
        ),
    )


def service_networking(request):
    return _render_service_page(request, "networking")


def service_security(request):
    return _render_service_page(request, "security")


def service_development(request):
    return _render_service_page(request, "development")


def service_automation(request):
    return _render_service_page(request, "automation")


def service_ai_cameras(request):
    return _render_service_page(request, "ai_cameras")


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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Builders & construction", "construction"),
            ),
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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Our approach to camera privacy", "camera_privacy"),
            ),
        ),
    )


def service_support(request):
    return _render_service_page(
        request,
        "support",
        plan_grids=[
            {"audience": "home", "plans": care_plans("home")},
            {"audience": "business", "plans": care_plans("business")},
        ],
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
        if (
            not _rate_limited(request, form, bucket="contact")
            and _passes_recaptcha(request, form, label="contact")
            and form.is_valid()
        ):
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
        plan = request.GET.get("plan", "").strip().lower()
        plan_lookup = {t["key"]: t["name"] for t in CARE_TIERS}
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
    return _render_thanks_page(request, "contact_thanks")


@require_http_methods(["GET", "POST"])
def careers(request):
    if request.method == "POST":
        form = JobApplicationForm(request.POST, request.FILES)
        if (
            not _rate_limited(request, form, bucket="careers")
            and _passes_recaptcha(request, form, label="careers")
            and form.is_valid()
        ):
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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Careers", "careers"),
            ),
            roles=JOB_ROLES,
            form=form,
        ),
    )


def careers_thanks(request):
    return _render_thanks_page(request, "careers_thanks")


def blog(request):
    posts = BlogPost.published.all()
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    # Page 2+ must self-canonicalise. Previously every page canonicalised to
    # /blog/, telling Google page 2 was a duplicate of page 1 and hiding the
    # only entry point to older posts. Built from the validated page number,
    # never request.get_full_path, so arbitrary query strings can't leak in.
    canonical_path = reverse("blog")
    if page_obj.number > 1:
        canonical_path = f"{canonical_path}?page={page_obj.number}"
    return render(
        request,
        "blog/list.html",
        _base_context(
            active="blog",
            canonical_path=canonical_path,
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
            related_services=_related_services(post.pillar),
            area_links=_area_links(),
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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Areas", "areas"),
            ),
        ),
    )


def area_marlow(request):
    return _render_area_page(request, "marlow")


def area_maidenhead(request):
    return _render_area_page(request, "maidenhead")


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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Terms", "terms"),
            ),
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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Privacy", "privacy"),
            ),
        ),
    )


def area_henley(request):
    return _render_area_page(request, "henley")


def area_beaconsfield(request):
    return _render_area_page(request, "beaconsfield")


# --- Quote request ---

@require_http_methods(["GET", "POST"])
def quote(request):
    """Structured quote-request landing page. Captures property type,
    postcode, services, timeline and budget — more qualifying data than the
    generic contact form so we can reply with a real survey slot.
    """
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if (
            not _rate_limited(request, form, bucket="quote")
            and _passes_recaptcha(request, form, label="quote")
            and form.is_valid()
        ):
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
            breadcrumbs=_crumbs(
                ("Home", "home"),
                ("Get a quote", "quote"),
            ),
            form=form,
        ),
    )


def quote_thanks(request):
    return _render_thanks_page(request, "quote_thanks")


def healthz(request):
    return HttpResponse("ok\n", content_type="text/plain")
