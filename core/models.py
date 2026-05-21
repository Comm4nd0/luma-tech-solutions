import re

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


SERVICE_CHOICES = [
    ("networking", "Wi-Fi & Networking"),
    ("development", "App & Web Development"),
    ("automation", "Home Automation"),
    ("support", "Support & Maintenance"),
    ("other", "Something else"),
]


AUDIENCE_CHOICES = [
    ("home", "Home"),
    ("business", "Business"),
]


JOB_ROLE_CHOICES = [
    ("network", "UniFi Network Engineer"),
    ("infrastructure", "Infrastructure Engineer (Cable Installations)"),
    ("cyber", "Cyber Security Engineer"),
]


PILLAR_CHOICES = [
    ("networking", "Wi-Fi & Networking"),
    ("security", "Physical Security"),
    ("development", "App & Web Development"),
    ("automation", "Home Automation"),
    ("support", "Support & Maintenance"),
    ("general", "General"),
]


# Property / premises types — covers both residential and commercial so a
# single quote form can serve homes and businesses.
PROPERTY_TYPE_CHOICES = [
    ("home_small", "Home — under 150 m²"),
    ("home_medium", "Home — 150–300 m²"),
    ("home_large", "Home — 300 m² or larger"),
    ("home_period", "Period or listed home"),
    ("home_estate", "Estate or multi-building property"),
    ("business_office", "Business — office"),
    ("business_retail", "Business — retail / hospitality"),
    ("business_other", "Business — something else"),
    ("other", "Something else"),
]


# Services someone might want quoted. Mirrors the service pillars but is a
# separate list so we can evolve the marketing taxonomy without breaking
# stored quote rows.
QUOTE_SERVICE_CHOICES = [
    ("networking", "Wi-Fi & Networking"),
    ("security", "CCTV / Physical Security"),
    ("automation", "Smart Home / Home Automation"),
    ("development", "App or Website Build"),
    ("support", "Ongoing Support / Care Plan"),
    ("survey", "Site Survey only"),
    ("other", "Something else"),
]


TIMELINE_CHOICES = [
    ("urgent", "Within 2 weeks"),
    ("soon", "Within the next month"),
    ("planned", "1–3 months"),
    ("flexible", "Flexible / just exploring"),
]


BUDGET_CHOICES = [
    ("under_2k", "Under £2,000"),
    ("2k_5k", "£2,000 – £5,000"),
    ("5k_15k", "£5,000 – £15,000"),
    ("15k_50k", "£15,000 – £50,000"),
    ("50k_plus", "£50,000+"),
    ("not_sure", "Not sure yet"),
]


class ContactSubmission(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    audience = models.CharField(
        max_length=16, choices=AUDIENCE_CHOICES, blank=True, default=""
    )
    service = models.CharField(max_length=32, choices=SERVICE_CHOICES, default="other")
    message = models.TextField()
    source = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Internal tag identifying which page/CTA the enquiry came from.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_service_display()}"


class JobApplication(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    role = models.CharField(max_length=32, choices=JOB_ROLE_CHOICES)
    cover_note = models.TextField(blank=True)
    cv_filename = models.CharField(max_length=255, blank=True)
    cv_size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_role_display()}"


class QuoteRequest(models.Model):
    """A structured quote enquiry — more qualifying detail than the generic
    contact form. Routed to the same inbox by default, but stored separately
    so we can see and report on the dedicated funnel.
    """

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    postcode = models.CharField(
        max_length=16,
        help_text="UK postcode — used to confirm the property is in our coverage area.",
    )
    property_type = models.CharField(
        max_length=32, choices=PROPERTY_TYPE_CHOICES, default="other"
    )
    # Comma-separated list of QUOTE_SERVICE_CHOICES keys — a single quote can
    # cover more than one service (Wi-Fi + CCTV is common).
    services = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Comma-separated service keys, e.g. 'networking,security'.",
    )
    timeline = models.CharField(
        max_length=16, choices=TIMELINE_CHOICES, blank=True, default=""
    )
    budget = models.CharField(
        max_length=16, choices=BUDGET_CHOICES, blank=True, default=""
    )
    notes = models.TextField(blank=True)
    source = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Internal tag identifying which page/CTA the enquiry came from.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_property_type_display()}"

    def services_display(self):
        """Human-readable list of selected services, in the canonical order
        defined by QUOTE_SERVICE_CHOICES.
        """
        if not self.services:
            return ""
        chosen = {s.strip() for s in self.services.split(",") if s.strip()}
        labels = [label for key, label in QUOTE_SERVICE_CHOICES if key in chosen]
        return ", ".join(labels)


class PublishedBlogManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(published_at__isnull=False, published_at__lte=timezone.now())
        )


_HTML_TAG_RE = re.compile(r"<[^>]+>")


class BlogPost(models.Model):
    title = models.CharField(max_length=240)
    slug = models.SlugField(max_length=260, unique=True, blank=True)
    content = models.TextField(help_text="Rendered as HTML.")
    excerpt = models.CharField(
        max_length=400,
        help_text="Short summary shown on the blog listing.",
    )
    author = models.CharField(max_length=120, default="Marco Baldanza")
    pillar = models.CharField(
        max_length=20, choices=PILLAR_CHOICES, default="general"
    )
    meta_description = models.CharField(
        max_length=200,
        blank=True,
        help_text="Used in <meta name=description>. Leave blank to fall back to the excerpt.",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Leave blank to keep as a draft. Set a future date to schedule.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedBlogManager()

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:260]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_post", kwargs={"slug": self.slug})

    @property
    def reading_time_minutes(self):
        words = len(_HTML_TAG_RE.sub(" ", self.content or "").split())
        return max(1, round(words / 220))

    @property
    def first_image(self):
        if not self.content:
            return None
        tag = re.search(r"<img\b[^>]*>", self.content, re.IGNORECASE)
        if not tag:
            return None
        src = re.search(r'\bsrc="([^"]+)"', tag.group(0), re.IGNORECASE)
        if not src:
            return None
        alt = re.search(r'\balt="([^"]*)"', tag.group(0), re.IGNORECASE)
        return {"src": src.group(1), "alt": (alt.group(1) if alt else self.title) or ""}

    @property
    def seo_description(self):
        return (self.meta_description or self.excerpt)[:200]

    @property
    def is_published(self):
        return bool(
            self.published_at and self.published_at <= timezone.now()
        )
