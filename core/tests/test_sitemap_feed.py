"""Sitemap, RSS feed and robots.txt."""
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost


class SitemapFeedTests(TestCase):
    def setUp(self):
        BlogPost.objects.all().delete()
        self.post = BlogPost.objects.create(
            title="Published Post", excerpt="x", content="<p>a</p>",
            published_at=timezone.now() - timedelta(days=1),
        )
        self.draft = BlogPost.objects.create(
            title="Draft Post", excerpt="x", content="<p>a</p>",
            published_at=None,
        )

    def test_sitemap_lists_published_post_and_static_pages(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn(f"/blog/{self.post.slug}/", body)
        self.assertNotIn(f"/blog/{self.draft.slug}/", body)
        self.assertIn("/services/", body)

    def test_feed_lists_published_post(self):
        resp = self.client.get(reverse("blog_feed"))
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn("Published Post", body)
        self.assertNotIn("Draft Post", body)

    def test_robots_txt(self):
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/plain", resp["Content-Type"])
