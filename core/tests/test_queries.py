"""Query-count and coverage guards.

There were no assertNumQueries assertions anywhere, so a query regression on
the blog pages would have been invisible.
"""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.content import (
    AREA_PAGES,
    CASE_STUDIES,
    SERVICE_PAGES,
    THANKS_PAGES,
    area_is_draft,
)
from core.models import BlogPost
from core.sitemaps import StaticViewSitemap


class BlogQueryCountTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        BlogPost.objects.bulk_create(
            BlogPost(
                title=f"Query test post {i}",
                slug=f"query-test-post-{i}",
                content=f"<p>Body {i}</p>",
                excerpt=f"Body {i}",
                pillar="networking" if i % 2 else "security",
                published_at=timezone.now(),
            )
            for i in range(25)
        )

    def test_blog_list_is_two_queries_regardless_of_page_size(self):
        # Paginator COUNT(*) + the page itself. first_image and
        # reading_time_minutes are cached_property, so rendering ten cards
        # adds nothing.
        with self.assertNumQueries(2):
            resp = self.client.get(reverse("blog"))
            self.assertEqual(resp.status_code, 200)

    def test_blog_page_two_is_also_two_queries(self):
        with self.assertNumQueries(2):
            resp = self.client.get(reverse("blog") + "?page=2")
            self.assertEqual(resp.status_code, 200)

    def test_blog_detail_is_two_queries(self):
        # The post, plus the related-posts lookup.
        post = BlogPost.published.first()
        with self.assertNumQueries(2):
            resp = self.client.get(post.get_absolute_url())
            self.assertEqual(resp.status_code, 200)

    def test_feed_is_one_query(self):
        with self.assertNumQueries(1):
            self.assertEqual(self.client.get(reverse("blog_feed")).status_code, 200)

    def test_static_pages_hit_the_database_zero_times(self):
        # Marketing content lives in core/content.py, not the DB.
        for name in ("home", "services", "service_networking", "area_marlow", "about"):
            with self.subTest(page=name):
                with self.assertNumQueries(0):
                    self.assertEqual(self.client.get(reverse(name)).status_code, 200)


class ContentTableCoverageTests(TestCase):
    """Every entry in a page table must resolve to a real, working URL, so a
    table can't grow an orphan that nothing renders."""

    def test_every_service_page_entry_resolves(self):
        for key, page in SERVICE_PAGES.items():
            with self.subTest(service=key):
                resp = self.client.get(reverse(page["url_name"]))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.templates[0].name, page["template"])

    def test_every_area_page_entry_resolves(self):
        for key, page in AREA_PAGES.items():
            with self.subTest(area=key):
                resp = self.client.get(reverse(page["url_name"]))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.templates[0].name, page["template"])

    def test_every_thanks_page_entry_resolves(self):
        for key, page in THANKS_PAGES.items():
            with self.subTest(page=key):
                resp = self.client.get(reverse(key))
                self.assertEqual(resp.status_code, 200)
                self.assertEqual(resp.templates[0].name, page["template"])


class SitemapCoverageTests(TestCase):
    def test_every_service_and_area_page_is_in_the_sitemap(self):
        # A new page added to the tables must not silently miss the sitemap.
        # items() yields (url_name, priority) tuples.
        #
        # Draft area pages are the one exception: they are served noindex
        # while their local copy is still placeholder, so listing them would
        # ask Google to index a page we have just told it not to.
        listed = {name for name, _priority in StaticViewSitemap().items()}
        for key, page in SERVICE_PAGES.items():
            with self.subTest(page=key):
                self.assertIn(page["url_name"], listed)
        for key, page in AREA_PAGES.items():
            with self.subTest(page=key):
                if area_is_draft(page):
                    self.assertNotIn(page["url_name"], listed)
                else:
                    self.assertIn(page["url_name"], listed)

    def test_thanks_pages_are_excluded(self):
        listed = {name for name, _priority in StaticViewSitemap().items()}
        for name in THANKS_PAGES:
            with self.subTest(page=name):
                self.assertNotIn(name, listed)

    def test_every_case_study_is_in_the_sitemap(self):
        resp = self.client.get("/sitemap.xml")
        for case in CASE_STUDIES:
            with self.subTest(slug=case["slug"]):
                self.assertContains(resp, reverse("case_study", args=[case["slug"]]))
