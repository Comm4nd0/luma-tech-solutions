"""Characterisation tests: every page's rendered contract, pinned.

These exist so the content-extraction and data-driven-view refactors can be
proved behaviour-preserving. Django renders a missing context variable as an
empty string, so a dropped context key is otherwise silent — hence the exact
comparison against ``page_contract.json``.

If you deliberately change a page's title, breadcrumbs, nav slot or schema,
update the fixture in the same commit. If you didn't mean to change it, the
diff is the bug.
"""

import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape

CONTRACT_PATH = Path(__file__).parent / "page_contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def ld_blocks(html):
    """Raw text of every application/ld+json block on the page."""
    blocks = []
    marker = 'type="application/ld+json"'
    pos = 0
    while True:
        idx = html.find(marker, pos)
        if idx == -1:
            return blocks
        start = html.index(">", idx) + 1
        end = html.index("</script>", start)
        blocks.append(html[start:end])
        pos = end


class PageContractTests(TestCase):
    """Each page still renders the same template with the same context."""

    def test_contract_covers_every_expected_page(self):
        # Guards against a page quietly dropping out of the fixture.
        self.assertEqual(len(CONTRACT), 26)

    def test_pages_match_pinned_contract(self):
        for name, expected in CONTRACT.items():
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.templates[0].name, expected["template"])

                ctx = resp.context
                for key in (
                    "active_nav",
                    "page_title",
                    "page_description",
                    "service_name",
                    "service_type",
                    "service_url",
                    "service_description",
                    "whatsapp_prefill",
                ):
                    if key in expected:
                        self.assertEqual(ctx[key], expected[key], msg=key)
                    else:
                        # Absent or None — both mean "this page doesn't set it".
                        self.assertIsNone(
                            ctx.get(key), msg=f"{name} unexpectedly sets {key}"
                        )

                if "breadcrumbs" in expected:
                    self.assertEqual(
                        [list(c) for c in ctx["breadcrumbs"]],
                        expected["breadcrumbs"],
                    )
                else:
                    self.assertIsNone(ctx.get("breadcrumbs"))

                if "faqs" in expected:
                    self.assertEqual(
                        [f["q"] for f in ctx["faqs"]], expected["faqs"]
                    )
                else:
                    # A page with no FAQs must not grow a FAQPage block.
                    self.assertIsNone(ctx.get("faqs"))
                    self.assertNotContains(resp, '"@type": "FAQPage"')

                if "featured_case" in expected:
                    self.assertEqual(
                        ctx["featured_case"]["slug"], expected["featured_case"]
                    )

                if "plan_grids" in expected:
                    self.assertEqual(
                        [
                            {
                                "audience": g["audience"],
                                "plans": [p["name"] for p in g["plans"]],
                            }
                            for g in ctx["plan_grids"]
                        ],
                        expected["plan_grids"],
                    )

    def test_security_page_owns_its_own_nav_slot(self):
        # Easy to lose when the five service views are collapsed into a table:
        # this is the only service page that is NOT active_nav="services".
        resp = self.client.get(reverse("service_security"))
        self.assertEqual(resp.context["active_nav"], "security")

    def test_pages_without_faqs_stay_without_faqs(self):
        for name in ("service_development", "service_automation", "service_support"):
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                self.assertIsNone(resp.context.get("faqs"))
                self.assertNotContains(resp, '"@type": "FAQPage"')


class AreaPageTests(TestCase):
    """The four town pages share a sidebar and a schema partial but must not
    converge on the same content — that is the point of local landing pages."""

    def test_beaconsfield_keeps_its_distinct_offer(self):
        # Beaconsfield is the only town promising a free survey and a 48h
        # proposal. Hard-coding the Marlow wording in the shared sidebar would
        # silently rewrite it.
        resp = self.client.get(reverse("area_beaconsfield"))
        self.assertContains(resp, "Free on-site survey")
        self.assertContains(resp, "Fixed-price proposal in 48h")

        for name in ("area_marlow", "area_maidenhead", "area_henley"):
            with self.subTest(page=name):
                other = self.client.get(reverse(name))
                self.assertNotContains(other, "Free on-site survey")
                self.assertNotContains(other, "Fixed-price proposal in 48h")

    def test_no_faq_is_shared_between_towns(self):
        # Four town pages answering the same four questions in the same words
        # is the near-duplicate set these pages exist to avoid. Copying one
        # town's FAQ block to another is the easy way to recreate it.
        from core.content import AREA_FAQS

        seen = {}
        for town, faqs in AREA_FAQS.items():
            for faq in faqs:
                for field in ("q", "a"):
                    text = faq[field]
                    self.assertNotIn(
                        text, seen, msg=f"{town} repeats {seen.get(text)}: {text!r}"
                    )
                    seen[text] = town

    def test_every_town_page_renders_its_own_faqs(self):
        from core.content import AREA_FAQS

        for key, faqs in AREA_FAQS.items():
            with self.subTest(town=key):
                resp = self.client.get(reverse(f"area_{key}"))
                self.assertContains(resp, '"@type": "FAQPage"')
                for faq in faqs:
                    self.assertContains(resp, escape(faq["q"]))

    def test_each_town_declares_only_its_own_city(self):
        # The shared _service_schema.html declares every SITE_TOWNS entry plus
        # both counties. Reusing it here would broaden each town page's
        # areaServed to the whole region and undo the local-SEO targeting.
        expected = {
            "area_marlow": "Marlow",
            "area_maidenhead": "Maidenhead",
            "area_henley": "Henley-on-Thames",
            "area_beaconsfield": "Beaconsfield",
        }
        for name, town in expected.items():
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                blocks = [json.loads(b) for b in ld_blocks(resp.content.decode())]
                services = [b for b in blocks if b.get("@type") == "Service"]
                self.assertEqual(len(services), 1)
                self.assertEqual(
                    services[0]["areaServed"], {"@type": "City", "name": town}
                )


class StructuredDataTests(TestCase):
    """Every JSON-LD block on every page is valid JSON with sane URLs."""

    def test_every_jsonld_block_parses(self):
        for name in CONTRACT:
            resp = self.client.get(reverse(name))
            html = resp.content.decode()
            blocks = ld_blocks(html)
            self.assertTrue(blocks, msg=f"{name} has no JSON-LD at all")
            for i, raw in enumerate(blocks):
                with self.subTest(page=name, block=i):
                    json.loads(raw)

    def test_service_schema_urls_are_paths_not_url_names(self):
        # reverse() returns "/services/networking/"; passing the *url name*
        # instead renders "https://…co.ukservice_networking", which is valid
        # HTML and valid JSON, and nothing else would catch it.
        for name, expected in CONTRACT.items():
            if "service_url" not in expected:
                continue
            with self.subTest(page=name):
                self.assertTrue(
                    expected["service_url"].startswith("/"),
                    msg=f"{name} service_url is not a path",
                )
                resp = self.client.get(reverse(name))
                html = resp.content.decode()
                for raw in ld_blocks(html):
                    data = json.loads(raw)
                    if data.get("@type") != "Service":
                        continue
                    self.assertTrue(
                        data["url"].startswith(settings.SITE_URL + "/"),
                        msg=f"{name} Service.url = {data['url']!r}",
                    )
                    self.assertTrue(data["name"])
                    self.assertTrue(data["serviceType"])
                    self.assertTrue(data["description"])
