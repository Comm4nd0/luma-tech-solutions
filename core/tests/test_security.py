"""CSP header/nonce and Google Ads consent gating."""
import re

from django.test import TestCase, override_settings
from django.urls import reverse


class CspHeaderTests(TestCase):
    def test_csp_header_present_with_strict_script_src(self):
        resp = self.client.get(reverse("home"))
        csp = resp.headers.get("Content-Security-Policy")
        self.assertIsNotNone(csp)
        self.assertIn("script-src", csp)
        self.assertIn("'strict-dynamic'", csp)
        self.assertIn("'nonce-", csp)
        self.assertIn("object-src 'none'", csp)

    def test_nonce_in_header_matches_body(self):
        resp = self.client.get(reverse("home"))
        csp = resp.headers["Content-Security-Policy"]
        nonce = re.search(r"'nonce-([^']+)'", csp).group(1)
        # The same nonce must appear on at least one script tag in the body.
        self.assertIn(f'nonce="{nonce}"', resp.content.decode())

    @override_settings(CSP_REPORT_ONLY=True)
    def test_report_only_toggle(self):
        resp = self.client.get(reverse("home"))
        self.assertIn("Content-Security-Policy-Report-Only", resp.headers)
        self.assertNotIn("Content-Security-Policy", resp.headers)


class ConsentGatingTests(TestCase):
    def test_gtag_library_not_loaded_unconditionally(self):
        body = self.client.get(reverse("home")).content.decode()
        # The tag library must NOT be hard-loaded; only the cookieless shim is.
        self.assertNotIn("googletagmanager.com/gtag/js", body)
        self.assertIn("window.LUMA_ADS_ID", body)

    def test_thanks_page_queues_conversion_without_loading_library(self):
        body = self.client.get(reverse("contact_thanks")).content.decode()
        self.assertIn("'conversion'", body)
        self.assertNotIn("googletagmanager.com/gtag/js", body)
