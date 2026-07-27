"""Every route returns 200.

Before this existed, roughly 25 of the 31 views had no test at all — a broken
template on four of the five showcase demos, any area page or the blog would
have shipped to production unnoticed (the deploy workflow smoke-tests exactly
one showcase demo).
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost
from core.views import CASE_STUDIES, WEBSITE_DEMOS

# Routes that take no arguments and render HTML.
SIMPLE_ROUTES = [
    "home", "services", "service_networking", "service_security",
    "service_ai_cameras", "camera_privacy", "service_development",
    "service_automation", "service_support", "construction",
    "capability_statement", "about", "portfolio", "areas", "area_marlow",
    "area_maidenhead", "area_henley", "area_beaconsfield", "contact",
    "contact_thanks", "quote", "quote_thanks", "careers", "careers_thanks",
    "terms", "privacy", "blog",
]


class SmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = BlogPost.objects.create(
            title="Smoke test post",
            content="<p>Body.</p>",
            excerpt="Body.",
            pillar="networking",
            published_at=timezone.now(),
        )

    def test_simple_routes_return_200(self):
        for name in SIMPLE_ROUTES:
            with self.subTest(route=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_every_case_study_detail_renders(self):
        for case in CASE_STUDIES:
            with self.subTest(slug=case["slug"]):
                resp = self.client.get(reverse("case_study", args=[case["slug"]]))
                self.assertEqual(resp.status_code, 200)

    def test_every_showcase_demo_renders(self):
        # The deploy smoke test only curls maple-and-vine; the other four
        # would break silently.
        for demo in WEBSITE_DEMOS:
            with self.subTest(slug=demo["slug"]):
                resp = self.client.get(reverse("showcase_demo", args=[demo["slug"]]))
                self.assertEqual(resp.status_code, 200)

    def test_blog_detail_renders(self):
        resp = self.client.get(reverse("blog_post", args=[self.post.slug]))
        self.assertEqual(resp.status_code, 200)

    def test_draft_post_is_404(self):
        draft = BlogPost.objects.create(
            title="Unpublished draft", content="<p>x</p>", excerpt="x"
        )
        resp = self.client.get(reverse("blog_post", args=[draft.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_unknown_slugs_are_404(self):
        for name in ("case_study", "showcase_demo", "blog_post"):
            with self.subTest(route=name):
                resp = self.client.get(reverse(name, args=["no-such-thing"]))
                self.assertEqual(resp.status_code, 404)

    def test_non_html_routes(self):
        self.assertEqual(self.client.get(reverse("healthz")).status_code, 200)
        self.assertEqual(self.client.get(reverse("robots")).status_code, 200)
        self.assertEqual(self.client.get(reverse("blog_feed")).status_code, 200)
        self.assertEqual(self.client.get("/sitemap.xml").status_code, 200)

    def test_blog_pagination_second_page_renders(self):
        BlogPost.objects.bulk_create(
            BlogPost(
                title=f"Filler post {i}",
                slug=f"filler-post-{i}",
                content="<p>x</p>",
                excerpt="x",
                pillar="general",
                published_at=timezone.now(),
            )
            for i in range(12)
        )
        resp = self.client.get(reverse("blog") + "?page=2")
        self.assertEqual(resp.status_code, 200)
