"""Enquiries are never lost to the spam check or to a failed email."""
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import ContactSubmission, JobApplication, QuoteRequest

CONTACT = {
    "name": "Jo", "email": "jo@example.com", "service": "networking",
    "message": "Wi-Fi drops upstairs",
}
QUOTE = {
    "name": "Jo", "email": "jo@example.com", "postcode": "SL7 1AA",
    "services": ["networking"],
}
FLAGGED = (False, 0.1, "low score 0.10")


@override_settings(RECAPTCHA_SECRET_KEY="x")
class FlaggedEnquiryTests(TestCase):
    @mock.patch("core.views._verify_recaptcha", return_value=FLAGGED)
    def test_low_score_contact_is_saved_and_emailed(self, _m):
        resp = self.client.post(reverse("contact"), CONTACT)
        self.assertRedirects(resp, reverse("contact_thanks"))
        row = ContactSubmission.objects.get()
        self.assertTrue(row.suspected_spam)
        self.assertEqual(row.spam_reason, "low score 0.10")
        self.assertTrue(row.notified)
        self.assertIn("[Possible spam]", mail.outbox[0].subject)
        self.assertIn("low score 0.10", mail.outbox[0].body)

    @mock.patch("core.views._verify_recaptcha", return_value=FLAGGED)
    def test_low_score_quote_is_saved_and_emailed(self, _m):
        resp = self.client.post(reverse("quote"), QUOTE)
        self.assertRedirects(resp, reverse("quote_thanks"))
        self.assertTrue(QuoteRequest.objects.get().suspected_spam)
        self.assertIn("[Possible spam]", mail.outbox[0].subject)

    def test_missing_token_is_saved(self):
        """An ad blocker stops the browser ever getting a token."""
        self.client.post(reverse("contact"), CONTACT)
        row = ContactSubmission.objects.get()
        self.assertEqual(row.spam_reason, "missing token")

    @mock.patch("urllib.request.urlopen", side_effect=OSError("google down"))
    def test_google_outage_is_saved(self, _m):
        self.client.post(reverse("quote"), {**QUOTE, "g-recaptcha-response": "t"})
        self.assertEqual(QuoteRequest.objects.get().spam_reason, "verification error")

    @mock.patch("core.views._verify_recaptcha", return_value=FLAGGED)
    def test_flagged_enquiry_is_not_a_conversion(self, _m):
        resp = self.client.post(reverse("contact"), CONTACT, follow=True)
        self.assertNotContains(resp, "Enquiry received")

    @mock.patch("core.views._verify_recaptcha", return_value=(True, 0.9, "ok"))
    def test_clean_enquiry_is_a_conversion(self, _m):
        resp = self.client.post(reverse("contact"), CONTACT, follow=True)
        self.assertContains(resp, "Enquiry received")
        self.assertFalse(ContactSubmission.objects.get().suspected_spam)
        self.assertNotIn("Possible spam", mail.outbox[0].subject)

    @mock.patch("core.views._verify_recaptcha", return_value=FLAGGED)
    def test_honeypot_still_rejects(self, _m):
        resp = self.client.post(reverse("contact"), {**CONTACT, "website": "x"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)
        self.assertEqual(mail.outbox, [])

    @mock.patch("core.views._verify_recaptcha", return_value=FLAGGED)
    def test_invalid_enquiry_is_not_saved(self, _m):
        self.client.post(reverse("contact"), {**CONTACT, "email": "nope"})
        self.assertEqual(ContactSubmission.objects.count(), 0)

    @mock.patch("core.views._verify_recaptcha", return_value=FLAGGED)
    def test_careers_still_rejects(self, _m):
        cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        resp = self.client.post(reverse("careers"), {
            "name": "A", "email": "a@example.com", "role": "network", "cv": cv,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(JobApplication.objects.count(), 0)


class RetryLeadNotificationsTests(TestCase):
    def _row(self, age, model=ContactSubmission, **fields):
        defaults = (
            {"name": "Jo", "email": "jo@example.com", "message": "Hi"}
            if model is ContactSubmission
            else {"name": "Jo", "email": "jo@example.com", "postcode": "SL7 1AA",
                  "property_type": "home_unsure", "services": "networking"}
        )
        row = model.objects.create(**{**defaults, **fields})
        model.objects.filter(pk=row.pk).update(created_at=timezone.now() - age)
        return row

    def _run(self):
        out = StringIO()
        call_command("retry_lead_notifications", stdout=out)
        return out.getvalue()

    def test_resends_failed_contact_and_quote(self):
        contact = self._row(timedelta(hours=1))
        quote = self._row(timedelta(hours=1), model=QuoteRequest)
        self.assertIn("2 resent", self._run())
        contact.refresh_from_db()
        quote.refresh_from_db()
        self.assertTrue(contact.notified and quote.notified)
        self.assertTrue(all("[Delayed]" in m.subject for m in mail.outbox))

    def test_does_not_send_twice(self):
        self._row(timedelta(hours=1))
        self._run()
        self._run()
        self.assertEqual(len(mail.outbox), 1)

    def test_skips_delivered_too_recent_and_too_old(self):
        self._row(timedelta(hours=1), notified=True)
        self._row(timedelta(minutes=1))
        self._row(timedelta(days=8))
        self.assertIn("0 resent", self._run())
        self.assertEqual(mail.outbox, [])

    @mock.patch("core.views._notify", return_value=False)
    def test_failure_leaves_the_row_for_the_next_run(self, _m):
        row = self._row(timedelta(hours=1))
        self.assertIn("1 still failing", self._run())
        row.refresh_from_db()
        self.assertFalse(row.notified)


class EnquiryAdminTests(TestCase):
    def setUp(self):
        self.client.force_login(get_user_model().objects.create_superuser("a", "a@b.com", "p"))
        self.url = reverse("admin:core_contactsubmission_changelist")

    def _row(self, **fields):
        return ContactSubmission.objects.create(
            name="Jo", email="j@example.com", message="Hi", **fields)

    def test_warns_about_undelivered_enquiries(self):
        self._row()
        self.assertContains(self.client.get(self.url), "never reached your inbox")

    def test_no_warning_when_everything_delivered(self):
        self._row(notified=True)
        self.assertNotContains(self.client.get(self.url), "never reached your inbox")

    def test_possible_spam_is_left_out_of_lead_totals(self):
        self._row(notified=True)
        self._row(notified=True, suspected_spam=True, spam_reason="low score 0.10")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["lead_summary"]["enquiries"], 1)
        self.assertEqual(resp.context["lead_summary"]["possible_spam"], 1)


class TradingDisclosureTests(TestCase):
    def test_footer_shows_statutory_details_but_schema_does_not(self):
        html = self.client.get(reverse("home")).content.decode()
        footer = html[html.index('class="footer-legal"'):]
        for text in ("Luma Tech Solutions Ltd", "England and Wales", "12644409", "PE6 8FD"):
            self.assertIn(text, footer)
        self.assertEqual(html.count("PE6 8FD"), 1)

    def test_vat_number_hidden_until_set(self):
        self.assertNotContains(self.client.get(reverse("home")), "VAT number")

    @override_settings(SITE_VAT_NUMBER="GB123456789")
    def test_vat_number_shown_when_set(self):
        self.assertContains(self.client.get(reverse("home")), "VAT number GB123456789")
