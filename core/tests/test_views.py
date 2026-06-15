"""Form-handling views: reCAPTCHA gating, email, CV persistence, admin download."""
import shutil
import tempfile
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import ContactSubmission, JobApplication, QuoteRequest

_MEDIA_TMP = tempfile.mkdtemp(prefix="luma-test-media-")


def tearDownModule():
    shutil.rmtree(_MEDIA_TMP, ignore_errors=True)


PDF = b"%PDF-1.4\n%test\n"


class ContactViewTests(TestCase):
    def test_valid_submission_saves_and_emails(self):
        resp = self.client.post(reverse("contact"), {
            "name": "Jo", "email": "jo@example.com", "service": "networking",
            "message": "Hello there",
        })
        self.assertRedirects(resp, reverse("contact_thanks"))
        sub = ContactSubmission.objects.get()
        self.assertTrue(sub.notified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].reply_to, ["jo@example.com"])

    def test_honeypot_blocks(self):
        resp = self.client.post(reverse("contact"), {
            "name": "Bot", "email": "b@x.com", "service": "other",
            "message": "spam", "website": "http://spam",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(RECAPTCHA_SECRET_KEY="x")
    @mock.patch("core.views._verify_recaptcha", return_value=(False, 0.1, "low"))
    def test_recaptcha_failure_blocks(self, _m):
        resp = self.client.post(reverse("contact"), {
            "name": "Jo", "email": "jo@example.com", "service": "networking",
            "message": "Hello",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ContactSubmission.objects.count(), 0)
        self.assertContains(resp, "couldn&#x27;t verify", status_code=200)


class QuoteViewTests(TestCase):
    def test_valid_quote_includes_budget_in_email(self):
        resp = self.client.post(reverse("quote"), {
            "name": "Jo", "email": "jo@example.com", "postcode": "sl7 1aa",
            "property_type": "home_large", "services": ["networking", "security"],
            "timeline": "soon", "budget": "5k_15k",
        })
        self.assertRedirects(resp, reverse("quote_thanks"))
        q = QuoteRequest.objects.get()
        self.assertEqual(q.budget, "5k_15k")
        self.assertEqual(q.postcode, "SL7 1AA")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("£5,000 – £15,000", mail.outbox[0].body)

    def test_requires_a_service(self):
        resp = self.client.post(reverse("quote"), {
            "name": "Jo", "email": "jo@example.com", "postcode": "SL7 1AA",
            "property_type": "home_large",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(QuoteRequest.objects.count(), 0)


@override_settings(MEDIA_ROOT=_MEDIA_TMP)
class CareersViewTests(TestCase):
    def _payload(self):
        return {
            "name": "Applicant", "email": "applicant@example.com",
            "role": "network", "cover_note": "Hi",
        }

    def test_application_persists_cv_and_emails_attachment(self):
        cv = SimpleUploadedFile("cv.pdf", PDF, content_type="application/pdf")
        resp = self.client.post(
            reverse("careers"), {**self._payload(), "cv": cv}
        )
        self.assertRedirects(resp, reverse("careers_thanks"))
        app = JobApplication.objects.get()
        self.assertTrue(app.notified)
        self.assertTrue(app.cv_file)  # file persisted to MEDIA_ROOT
        self.assertEqual(app.cv_file.read(), PDF)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 1)

    @mock.patch("core.views._notify", return_value=False)
    def test_cv_kept_when_email_fails(self, _m):
        cv = SimpleUploadedFile("cv.pdf", PDF, content_type="application/pdf")
        resp = self.client.post(
            reverse("careers"), {**self._payload(), "cv": cv}
        )
        self.assertRedirects(resp, reverse("careers_thanks"))
        app = JobApplication.objects.get()
        self.assertFalse(app.notified)        # email failed
        self.assertTrue(app.cv_file)          # but the CV is recoverable
        self.assertEqual(app.cv_file.read(), PDF)


@override_settings(MEDIA_ROOT=_MEDIA_TMP)
class AdminCvDownloadTests(TestCase):
    def setUp(self):
        self.app = JobApplication(name="A", email="a@b.com", role="network")
        self.app.cv_filename = "cv.pdf"
        self.app.cv_file.save("cv.pdf", ContentFile(PDF), save=True)
        self.url = reverse("admin:core_jobapplication_cv", args=[self.app.pk])

    def test_anonymous_cannot_download(self):
        resp = self.client.get(self.url)
        self.assertNotEqual(resp.status_code, 200)  # redirected to admin login

    def test_staff_can_download(self):
        User = get_user_model()
        User.objects.create_superuser("admin", "admin@x.com", "pw12345!")
        self.client.force_login(User.objects.get(username="admin"))
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("attachment", resp["Content-Disposition"])

    def test_staff_without_view_permission_is_denied(self):
        # is_staff alone must not be enough — needs the JobApplication view perm.
        User = get_user_model()
        user = User.objects.create_user(
            "helper", "helper@x.com", "pw12345!", is_staff=True
        )
        self.client.force_login(user)
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 403)
