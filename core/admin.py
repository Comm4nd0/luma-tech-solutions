from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.urls import path, reverse
from django.utils.html import format_html

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
    list_display = ("name", "email", "role", "cv_download", "created_at", "notified")
    list_filter = ("role", "notified", "created_at")
    search_fields = ("name", "email", "phone", "cover_note", "cv_filename")
    readonly_fields = ("created_at", "cv_filename", "cv_size_bytes", "cv_download")

    def get_urls(self):
        custom = [
            path(
                "<int:pk>/cv/",
                self.admin_site.admin_view(self.download_cv),
                name="core_jobapplication_cv",
            ),
        ]
        return custom + super().get_urls()

    @admin.display(description="CV")
    def cv_download(self, obj):
        if not obj.pk or not obj.cv_file:
            return "—"
        url = reverse("admin:core_jobapplication_cv", args=[obj.pk])
        return format_html('<a href="{}">Download {}</a>', url, obj.cv_filename or "CV")

    def download_cv(self, request, pk):
        # admin_view() only enforces is_staff; mirror the changelist's
        # per-model gate so an under-privileged staff user can't pull a CV by
        # iterating the pk when they can't even see the application list.
        obj = self.get_object(request, pk)
        if obj is None or not obj.cv_file:
            raise Http404("No CV on file for this application.")
        if not self.has_view_permission(request, obj):
            raise PermissionDenied
        return FileResponse(
            obj.cv_file.open("rb"),
            as_attachment=True,
            filename=obj.cv_filename or "cv",
        )


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
