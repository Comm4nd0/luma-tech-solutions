from django.contrib import admin

from .models import BlogPost, ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "created_at", "notified")
    list_filter = ("service", "notified", "created_at")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("created_at",)


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
