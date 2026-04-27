from django.contrib import admin

from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "created_at", "notified")
    list_filter = ("service", "notified", "created_at")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("created_at",)
