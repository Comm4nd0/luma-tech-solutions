from datetime import timedelta

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.conf import settings
from django.db.models import Count, F, Q, Sum
from django.utils import timezone
from django.urls import path, reverse
from django.utils.html import format_html

from .models import BlogPost, ContactSubmission, JobApplication, QuoteRequest


class FollowUpFilter(admin.SimpleListFilter):
    title = "follow-up"
    parameter_name = "follow_up"

    def lookups(self, request, model_admin):
        return [("due", "Due today or overdue"), ("week", "Next seven days")]

    def queryset(self, request, queryset):
        today = timezone.localdate()
        if self.value() == "due":
            return queryset.filter(follow_up_on__lte=today).exclude(stage="lost")
        if self.value() == "week":
            return queryset.filter(follow_up_on__range=(today, today + timedelta(days=7))).exclude(stage="lost")
        return queryset


class EnquiryAdmin(admin.ModelAdmin):
    change_list_template = "admin/core/enquiry_change_list.html"
    change_form_template = "admin/core/enquiry_change_form.html"
    readonly_fields = ("created_at", "estimated_margin")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    workflow_fields = ("stage", "follow_up_on", "installed_on", "project_value", "direct_cost", "estimated_margin", "care_plan", "review_requested_on", "internal_notes")
    attribution_fields = ("source", "referral", "utm_source", "utm_medium", "utm_campaign")

    def save_model(self, request, obj, form, change):
        if obj.stage == "installed" and (not change or "stage" in form.changed_data):
            if not obj.installed_on:
                obj.installed_on = timezone.localdate()
            if "follow_up_on" not in form.changed_data:
                obj.follow_up_on = obj.installed_on + timedelta(days=14)
        super().save_model(request, obj, form, change)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra = {**(extra_context or {}), "review_url": settings.SITE_GOOGLE_REVIEW_URL,
                 "partner_url": settings.SITE_URL + reverse("partners"),
                 "site_phone": settings.SITE_PHONE, "site_email": settings.SITE_EMAIL}
        return super().changeform_view(request, object_id, form_url, extra_context=extra)

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        if not getattr(response, "context_data", None) or "cl" not in response.context_data:
            return response
        qs = response.context_data["cl"].queryset
        accepted = Q(stage__in=("won", "installed"))
        known_margin = accepted & Q(project_value__isnull=False, direct_cost__isnull=False)
        totals = qs.aggregate(
            enquiries=Count("pk"), accepted=Count("pk", filter=accepted),
            installed=Count("pk", filter=Q(stage="installed")),
            care_plans=Count("pk", filter=accepted & ~Q(care_plan="")),
            revenue=Sum("project_value", filter=accepted),
            margin=Sum(F("project_value") - F("direct_cost"), filter=known_margin),
            margin_records=Count("pk", filter=known_margin),
        )
        totals["stages"] = list(qs.order_by().values("stage").annotate(total=Count("pk")))
        labels = dict(self.model.STAGES)
        for row in totals["stages"]:
            row["label"] = labels.get(row["stage"], row["stage"])
        service_field = "services" if self.model is QuoteRequest else "service"
        totals["sources"] = list(qs.order_by().values("source", "utm_source", service_field).annotate(
            total=Count("pk"), accepted=Count("pk", filter=accepted),
            revenue=Sum("project_value", filter=accepted),
        ).order_by("-total", "source", "utm_source", service_field)[:30])
        for row in totals["sources"]:
            row["service_label"] = row[service_field]
        response.context_data["lead_summary"] = totals
        return response


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(EnquiryAdmin):
    list_display = ("name", "service", "stage", "follow_up_on", "source", "referral", "care_plan", "created_at", "notified")
    list_filter = (FollowUpFilter, "stage", "service", "source", "utm_source", "care_plan", "notified", "created_at")
    search_fields = ("name", "email", "phone", "message", "source", "referral", "internal_notes")
    fieldsets = (
        ("Enquiry", {"fields": ("name", "email", "phone", "audience", "service", "message", "created_at", "notified")}),
        ("Progress and follow-up", {"fields": EnquiryAdmin.workflow_fields}),
        ("Source", {"fields": EnquiryAdmin.attribution_fields}),
    )


class QuoteServiceFilter(admin.SimpleListFilter):
    title = "service"
    parameter_name = "service"

    def lookups(self, request, model_admin):
        from .models import QUOTE_SERVICE_CHOICES
        return QUOTE_SERVICE_CHOICES

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(Q(services=value) | Q(services__startswith=value + ",") | Q(services__endswith="," + value) | Q(services__contains="," + value + ","))
        return queryset


@admin.register(QuoteRequest)
class QuoteRequestAdmin(EnquiryAdmin):
    list_display = ("name", "postcode", "services_display", "stage", "follow_up_on", "source", "care_plan", "created_at", "notified")
    list_filter = (FollowUpFilter, QuoteServiceFilter, "stage", "property_type", "source", "utm_source", "care_plan", "notified", "created_at")
    search_fields = ("name", "email", "phone", "postcode", "notes", "source", "referral", "internal_notes")
    fieldsets = (
        ("Enquiry", {"fields": ("name", "email", "phone", "postcode", "property_type", "services", "timeline", "budget", "notes", "created_at", "notified")}),
        ("Progress and follow-up", {"fields": EnquiryAdmin.workflow_fields}),
        ("Source", {"fields": EnquiryAdmin.attribution_fields}),
    )


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
