"""Resend lead emails that failed when the enquiry was submitted.

Run every 15 minutes by the ``notifier`` service in docker-compose.yml.
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import ContactSubmission, QuoteRequest
from core.views import send_contact_notification, send_quote_notification

log = logging.getLogger(__name__)

# Leaves enquiries still being handled by the web process to finish first.
MIN_AGE = timedelta(minutes=5)
# Stops rows that predate this command from all being emailed at once.
MAX_AGE = timedelta(days=7)


class Command(BaseCommand):
    help = "Resend contact and quote emails that previously failed to send."

    def handle(self, *args, **options):
        now = timezone.now()
        window = {
            "notified": False,
            "created_at__gte": now - MAX_AGE,
            "created_at__lte": now - MIN_AGE,
        }
        sent = failed = 0
        for model, send in (
            (ContactSubmission, send_contact_notification),
            (QuoteRequest, send_quote_notification),
        ):
            for enquiry in model.objects.filter(**window).order_by("created_at"):
                if send(enquiry, delayed=True):
                    sent += 1
                else:
                    failed += 1
        if failed:
            log.error("%d lead notification(s) still failing", failed)
        self.stdout.write(f"Lead notifications: {sent} resent, {failed} still failing")
