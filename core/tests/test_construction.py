"""Builders & construction lead-gen pages: landing page, case-study detail,
capability statement, and the construction-specific form options."""
from django.test import TestCase
from django.urls import reverse

from core.models import QuoteRequest


class ConstructionPageTests(TestCase):
    def test_page_renders_with_key_sections(self):
        resp = self.client.get(reverse("construction"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "ANPR")
        self.assertContains(resp, "per plot")
        self.assertContains(resp, "Trade partners")
        self.assertContains(resp, "capability statement")
        # FAQPage JSON-LD comes from the shared FAQ partial.
        self.assertContains(resp, '"@type": "FAQPage"')

    def test_quote_ctas_prefill_construction_params(self):
        resp = self.client.get(reverse("construction"))
        self.assertContains(resp, "service=site_security")
        self.assertContains(resp, "property=construction_site")
        self.assertContains(resp, "service=prewire")

    def test_in_sitemap(self):
        resp = self.client.get("/sitemap.xml")
        self.assertContains(resp, reverse("construction"))


class CapabilityStatementTests(TestCase):
    def test_renders_standalone_and_noindexed(self):
        resp = self.client.get(reverse("capability_statement"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Capability statement")
        self.assertContains(resp, "noindex")
        # Standalone document — no site nav.
        self.assertNotContains(resp, "nav-links")


class CaseStudyDetailTests(TestCase):
    def test_detail_page_renders(self):
        resp = self.client.get(
            reverse("case_study", args=["chiltern-yard-anpr"])
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Chiltern Yard")
        self.assertContains(resp, "The full story")

    def test_unknown_slug_404s(self):
        resp = self.client.get(reverse("case_study", args=["not-a-case"]))
        self.assertEqual(resp.status_code, 404)

    def test_case_studies_in_sitemap(self):
        resp = self.client.get("/sitemap.xml")
        self.assertContains(
            resp, reverse("case_study", args=["chiltern-yard-anpr"])
        )


class ConstructionFormOptionTests(TestCase):
    def test_quote_accepts_construction_site_submission(self):
        resp = self.client.post(reverse("quote"), {
            "name": "Site Manager",
            "email": "sm@example.com",
            "postcode": "SL6 1AA",
            "property_type": "construction_site",
            "services": ["site_security", "prewire"],
            "timeline": "phased",
        })
        self.assertRedirects(resp, reverse("quote_thanks"))
        q = QuoteRequest.objects.get()
        self.assertEqual(q.property_type, "construction_site")
        self.assertIn("Site Security / ANPR", q.services_display())
        self.assertIn("Pre-wire / Structured Cabling", q.services_display())

    def test_quote_url_params_preselect_construction_options(self):
        resp = self.client.get(
            reverse("quote")
            + "?service=site_security,prewire&property=construction_site"
        )
        self.assertEqual(resp.status_code, 200)
        form = resp.context["form"]
        self.assertEqual(
            form.initial.get("services"), ["site_security", "prewire"]
        )
        self.assertEqual(
            form.initial.get("property_type"), "construction_site"
        )

    def test_contact_accepts_trade_audience_param(self):
        resp = self.client.get(reverse("contact") + "?audience=trade")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["form"].initial.get("audience"), "trade")
