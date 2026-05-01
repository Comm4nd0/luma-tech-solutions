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


PILLAR_CHOICES = [
    ("networking", "Wi-Fi & Networking"),
    ("security", "Security"),
    ("development", "App & Web Development"),
    ("automation", "Home Automation"),
    ("support", "Support & Maintenance"),
    ("general", "General"),
]


class ContactSubmission(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
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
    def seo_description(self):
        return (self.meta_description or self.excerpt)[:200]

    @property
    def is_published(self):
        return bool(
            self.published_at and self.published_at <= timezone.now()
        )
