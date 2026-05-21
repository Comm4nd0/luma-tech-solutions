from django.contrib import admin

from .models import BlogPost, ContactSubmission, JobApplication, QuoteRequest


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "source", "created_at", "notified")
    list_filter = ("service", "source", "notified", "created_at")
    search_fields = ("name", "email", "phone", "message", "source")
    readonly_fields = ("created_at",)


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = (
        "name", "email", "postcode", "property_type", "timeline",
        "budget", "source", "created_at", "notified",
    )
    list_filter = (
        "property_type", "timeline", "budget", "source", "notified", "created_at",
    )
    search_fields = ("name", "email", "phone", "postcode", "notes", "source")
    readonly_fields = ("created_at",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "role", "cv_filename", "created_at", "notified")
    list_filter = ("role", "notified", "created_at")
    search_fields = ("name", "email", "phone", "cover_note", "cv_filename")
    readonly_fields = ("created_at", "cv_filename", "cv_size_bytes")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "pillar", "published_at", "is_published", "updated_at")
    list_filter = ("pillar", "published_at")
    search_fields = ("title", "slug", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "pillar", "author")}),
        ("Content", {"fields": ("excerpt", "content")}),
        ("SEO", {"fields": ("meta_description",)}),
        ("Publishing", {"fields": ("published_at", "created_at", "updated_at")}),
    )

    @admin.display(boolean=True, description="Live")
    def is_published(self, obj):
        return obj.is_published
