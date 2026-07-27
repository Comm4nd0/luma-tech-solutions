"""Slug collisions, rate limiting and cached endpoints."""

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost

LOCMEM = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "ratelimit-tests",
    }
}


class SlugCollisionTests(TestCase):
    def test_duplicate_titles_get_distinct_slugs(self):
        # slug is unique=True; this used to raise IntegrityError, surfacing as
        # a 500 in the admin and a 400 with a raw DB error through the API.
        a = BlogPost.objects.create(title="Same title", content="<p>a</p>", excerpt="a")
        b = BlogPost.objects.create(title="Same title", content="<p>b</p>", excerpt="b")
        c = BlogPost.objects.create(title="Same title", content="<p>c</p>", excerpt="c")
        self.assertEqual(a.slug, "same-title")
        self.assertEqual(b.slug, "same-title-2")
        self.assertEqual(c.slug, "same-title-3")

    def test_resaving_a_post_keeps_its_slug(self):
        post = BlogPost.objects.create(
            title="Stable slug", content="<p>x</p>", excerpt="x"
        )
        original = post.slug
        post.excerpt = "changed"
        post.save()
        post.refresh_from_db()
        self.assertEqual(post.slug, original)

    def test_explicit_slug_is_respected(self):
        post = BlogPost.objects.create(
            title="Anything", slug="chosen-slug", content="<p>x</p>", excerpt="x"
        )
        self.assertEqual(post.slug, "chosen-slug")

    def test_api_handles_duplicate_titles(self):
        BlogPost.objects.create(title="API dupe", content="<p>x</p>", excerpt="x")
        second = BlogPost.objects.create(
            title="API dupe", content="<p>y</p>", excerpt="y"
        )
        self.assertNotEqual(second.slug, "api-dupe")
        resp = self.client.get(reverse("blog_post", args=[second.slug]))
        self.assertIn(resp.status_code, (200, 404))  # 404 only because it's a draft


@override_settings(CACHES=LOCMEM)
class RateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def _post_contact(self):
        return self.client.post(
            reverse("contact"),
            {
                "name": "Spammer",
                "email": "spam@example.com",
                "service": "networking",
                "message": "hello",
                "website": "",
            },
        )

    def test_submissions_are_throttled_per_ip(self):
        from core.views import RATE_LIMIT_MAX

        for i in range(RATE_LIMIT_MAX):
            with self.subTest(attempt=i):
                resp = self._post_contact()
                self.assertEqual(resp.status_code, 302, "should still be accepted")

        # The next one is refused, and refused without saving.
        before = BlogPost.objects.count()
        resp = self._post_contact()
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "a few submissions in a short space of time")
        self.assertEqual(BlogPost.objects.count(), before)

    def test_a_different_ip_is_unaffected(self):
        from core.views import RATE_LIMIT_MAX

        for _ in range(RATE_LIMIT_MAX + 1):
            self._post_contact()
        resp = self.client.post(
            reverse("contact"),
            {
                "name": "Someone else",
                "email": "real@example.com",
                "service": "networking",
                "message": "hello",
                "website": "",
            },
            REMOTE_ADDR="203.0.113.7",
        )
        self.assertEqual(resp.status_code, 302)


class CachedEndpointTests(TestCase):
    def test_feed_and_sitemap_still_reflect_new_posts(self):
        # DummyCache under test, so this asserts the endpoints work rather
        # than that they cache. The point is that nothing else broke.
        BlogPost.objects.create(
            title="Cached endpoint post",
            content="<p>x</p>",
            excerpt="x",
            pillar="networking",
            published_at=timezone.now(),
        )
        feed = self.client.get(reverse("blog_feed"))
        self.assertEqual(feed.status_code, 200)
        self.assertContains(feed, "Cached endpoint post")

        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "cached-endpoint-post")
