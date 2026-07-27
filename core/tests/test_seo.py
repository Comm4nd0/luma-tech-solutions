"""Indexing and social-metadata guarantees."""

import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import BlogPost
from core.tests.test_pages import ld_blocks


class RobotsTests(TestCase):
    def test_thanks_pages_are_noindex(self):
        # These fire the Google Ads conversion. An indexed thank-you page is
        # both a poor SERP result and a source of phantom conversions.
        for name in ("contact_thanks", "quote_thanks", "careers_thanks"):
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                self.assertContains(resp, 'content="noindex, nofollow"')
                self.assertNotContains(resp, 'content="index, follow"')

    def test_ordinary_pages_stay_indexable(self):
        for name in ("home", "services", "blog", "about", "area_marlow"):
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                self.assertContains(resp, 'content="index, follow"')
                self.assertNotContains(resp, "noindex")


class CanonicalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        BlogPost.objects.bulk_create(
            BlogPost(
                title=f"Canonical filler {i}",
                slug=f"canonical-filler-{i}",
                content="<p>x</p>",
                excerpt="x",
                pillar="general",
                published_at=timezone.now(),
            )
            for i in range(15)
        )

    def test_blog_page_one_canonicalises_to_itself(self):
        resp = self.client.get(reverse("blog"))
        self.assertContains(resp, f'rel="canonical" href="{settings.SITE_URL}/blog/"')

    def test_blog_page_two_canonicalises_to_page_two(self):
        # It used to canonicalise to /blog/, telling Google page 2 was a
        # duplicate of page 1 and hiding older posts' entry point.
        resp = self.client.get(reverse("blog") + "?page=2")
        self.assertContains(
            resp, f'rel="canonical" href="{settings.SITE_URL}/blog/?page=2"'
        )

    def test_arbitrary_query_strings_do_not_leak_into_canonical(self):
        # The naive fix (request.get_full_path) would make every tracking
        # parameter its own indexable URL.
        resp = self.client.get(reverse("blog") + "?utm_source=newsletter")
        self.assertContains(resp, f'rel="canonical" href="{settings.SITE_URL}/blog/"')
        self.assertNotContains(resp, "utm_source=newsletter&quot;")

    def test_other_pages_self_canonicalise(self):
        resp = self.client.get(reverse("service_networking"))
        self.assertContains(
            resp, f'rel="canonical" href="{settings.SITE_URL}/services/networking/"'
        )


class OpenGraphTests(TestCase):
    def test_blog_post_is_an_article_with_its_own_image(self):
        post = BlogPost.objects.create(
            title="Post with a hero image",
            content='<p>Intro.</p><img src="/static/img/blog/garden-wifi.jpg" alt="Garden Wi-Fi">',
            excerpt="Intro.",
            pillar="networking",
            published_at=timezone.now(),
        )
        resp = self.client.get(post.get_absolute_url())
        self.assertContains(resp, '<meta property="og:type" content="article" />')
        self.assertContains(
            resp,
            f'<meta property="og:image" content="{settings.SITE_URL}/static/img/blog/garden-wifi.jpg" />',
        )
        self.assertContains(
            resp,
            f'<meta name="twitter:image" content="{settings.SITE_URL}/static/img/blog/garden-wifi.jpg" />',
        )

    def test_blog_post_without_an_image_falls_back_to_the_site_card(self):
        # A {% block %} nested in an {% if %} is still always defined, so the
        # fallback has to live inside the block. Getting this wrong renders
        # og:image as a bare SITE_URL.
        post = BlogPost.objects.create(
            title="Post with no image",
            content="<p>Just text.</p>",
            excerpt="Just text.",
            pillar="general",
            published_at=timezone.now(),
        )
        resp = self.client.get(post.get_absolute_url())
        self.assertContains(
            resp,
            f'<meta property="og:image" content="{settings.SITE_URL}/static/img/og-default.png" />',
        )

    def test_non_article_pages_stay_website(self):
        resp = self.client.get(reverse("home"))
        self.assertContains(resp, '<meta property="og:type" content="website" />')

    def test_twitter_card_metadata_is_present(self):
        resp = self.client.get(reverse("home"))
        for tag in ("twitter:card", "twitter:title", "twitter:description", "twitter:image"):
            with self.subTest(tag=tag):
                self.assertContains(resp, tag)


class FounderSchemaTests(TestCase):
    def test_about_page_defines_the_founder_person_node(self):
        resp = self.client.get(reverse("about"))
        blocks = [json.loads(b) for b in ld_blocks(resp.content.decode())]
        people = [b for b in blocks if b.get("@type") == "Person"]
        self.assertEqual(len(people), 1)
        self.assertTrue(people[0]["@id"].endswith("#founder"))
        self.assertTrue(people[0]["name"])

    def test_organization_references_the_founder_by_id(self):
        resp = self.client.get(reverse("home"))
        blocks = [json.loads(b) for b in ld_blocks(resp.content.decode())]
        graphs = [b for b in blocks if "@graph" in b]
        self.assertTrue(graphs)
        org = next(
            n for n in graphs[0]["@graph"] if n.get("@type") == "Organization"
        )
        self.assertTrue(org["founder"]["@id"].endswith("#founder"))
