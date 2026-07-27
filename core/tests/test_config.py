"""Production configuration guards."""

from django.test import SimpleTestCase, override_settings

from core.checks import email_delivery_configured, recaptcha_configured


class EmailBackendCheckTests(SimpleTestCase):
    @override_settings(
        DEBUG=False,
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
    )
    def test_console_backend_in_production_is_flagged(self):
        ids = [w.id for w in email_delivery_configured(None)]
        self.assertIn("core.W001", ids)

    @override_settings(
        DEBUG=False,
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="",
    )
    def test_smtp_without_host_is_flagged(self):
        ids = [w.id for w in email_delivery_configured(None)]
        self.assertIn("core.W002", ids)

    @override_settings(
        DEBUG=False,
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="smtp.example.com",
        CONTACT_FORM_RECIPIENT="hello@example.com",
    )
    def test_correctly_configured_smtp_is_silent(self):
        self.assertEqual(email_delivery_configured(None), [])

    @override_settings(
        DEBUG=True,
        EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend",
    )
    def test_console_backend_in_debug_is_fine(self):
        self.assertEqual(email_delivery_configured(None), [])

    @override_settings(
        DEBUG=False,
        EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
        EMAIL_HOST="smtp.example.com",
        CONTACT_FORM_RECIPIENT="",
    )
    def test_missing_recipient_is_flagged(self):
        ids = [w.id for w in email_delivery_configured(None)]
        self.assertIn("core.W003", ids)


class RecaptchaCheckTests(SimpleTestCase):
    @override_settings(DEBUG=False, RECAPTCHA_SECRET_KEY="")
    def test_missing_secret_in_production_is_flagged(self):
        ids = [w.id for w in recaptcha_configured(None)]
        self.assertIn("core.W004", ids)

    @override_settings(DEBUG=False, RECAPTCHA_SECRET_KEY="a-real-key")
    def test_configured_secret_is_silent(self):
        self.assertEqual(recaptcha_configured(None), [])

    @override_settings(DEBUG=True, RECAPTCHA_SECRET_KEY="")
    def test_missing_secret_in_debug_is_fine(self):
        self.assertEqual(recaptcha_configured(None), [])
