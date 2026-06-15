"""Blog publishing JSON API: auth, CRUD, validation, sanitisation."""
import json

from django.test import TestCase, override_settings
from django.urls import reverse

from core.models import BlogPost

API_KEY = "test-key-0123456789-abcdefghij"
AUTH = f"Bearer {API_KEY}"


@override_settings(LUMA_BLOG_API_KEY=API_KEY)
class BlogApiTests(TestCase):
    def setUp(self):
        BlogPost.objects.all().delete()
        self.collection = reverse("api_blog_posts")

    def _post(self, payload, auth=AUTH):
        return self.client.post(
            self.collection, json.dumps(payload),
            content_type="application/json", HTTP_AUTHORIZATION=auth,
        )

    def _detail(self, slug):
        return reverse("api_blog_post", kwargs={"slug": slug})

    # --- auth ---
    def test_missing_auth_is_401(self):
        resp = self.client.get(self.collection)
        self.assertEqual(resp.status_code, 401)

    def test_wrong_key_is_401(self):
        resp = self.client.get(self.collection, HTTP_AUTHORIZATION="Bearer nope")
        self.assertEqual(resp.status_code, 401)

    @override_settings(LUMA_BLOG_API_KEY="")
    def test_unconfigured_key_is_503(self):
        resp = self.client.get(self.collection, HTTP_AUTHORIZATION=AUTH)
        self.assertEqual(resp.status_code, 503)

    # --- create ---
    def test_create_returns_201_and_derives_slug(self):
        resp = self._post({
            "title": "Hello World", "content": "<p>hi</p>", "excerpt": "x",
        })
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["slug"], "hello-world")
        self.assertFalse(body["is_published"])  # no published_at -> draft

    def test_create_sanitises_content(self):
        resp = self._post({
            "title": "XSS", "content": "<p>ok</p><script>steal()</script>",
            "excerpt": "x",
        })
        self.assertEqual(resp.status_code, 201)
        self.assertNotIn("<script", resp.json()["content"])
        self.assertNotIn("<script", BlogPost.objects.get(slug="xss").content)

    def test_create_slug_conflict_is_409(self):
        self._post({"title": "Dup", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "dup"})
        resp = self._post({"title": "Dup 2", "content": "<p>a</p>",
                           "excerpt": "x", "slug": "dup"})
        self.assertEqual(resp.status_code, 409)

    def test_create_unknown_field_is_400(self):
        resp = self._post({"title": "T", "content": "<p>a</p>", "excerpt": "x",
                           "bogus": 1})
        self.assertEqual(resp.status_code, 400)

    def test_create_bad_pillar_is_400(self):
        resp = self._post({"title": "T", "content": "<p>a</p>", "excerpt": "x",
                           "pillar": "nonsense"})
        self.assertEqual(resp.status_code, 400)

    def test_create_missing_required_is_400(self):
        resp = self._post({"title": "Only title"})
        self.assertEqual(resp.status_code, 400)

    def test_create_bad_published_at_is_400(self):
        resp = self._post({"title": "T", "content": "<p>a</p>", "excerpt": "x",
                           "published_at": "not-a-date"})
        self.assertEqual(resp.status_code, 400)

    # --- read ---
    def test_get_detail_includes_drafts(self):
        self._post({"title": "Draft", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "draft"})
        resp = self.client.get(self._detail("draft"), HTTP_AUTHORIZATION=AUTH)
        self.assertEqual(resp.status_code, 200)

    def test_get_missing_is_404(self):
        resp = self.client.get(self._detail("ghost"), HTTP_AUTHORIZATION=AUTH)
        self.assertEqual(resp.status_code, 404)

    def test_list_status_filter(self):
        self._post({"title": "D", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "d"})  # draft
        self._post({"title": "L", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "l", "published_at": "2020-01-01T00:00:00+00:00"})
        self._post({"title": "S", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "s", "published_at": "2999-01-01T00:00:00+00:00"})
        drafts = self.client.get(
            self.collection + "?status=draft", HTTP_AUTHORIZATION=AUTH
        ).json()
        self.assertEqual({p["slug"] for p in drafts["results"]}, {"d"})
        published = self.client.get(
            self.collection + "?status=published", HTTP_AUTHORIZATION=AUTH
        ).json()
        self.assertEqual({p["slug"] for p in published["results"]}, {"l"})
        scheduled = self.client.get(
            self.collection + "?status=scheduled", HTTP_AUTHORIZATION=AUTH
        ).json()
        self.assertEqual({p["slug"] for p in scheduled["results"]}, {"s"})

    # --- update ---
    def test_put_creates_then_updates(self):
        url = self._detail("upsert-me")
        resp = self.client.put(
            url, json.dumps({"title": "Up", "content": "<p>a</p>", "excerpt": "x"}),
            content_type="application/json", HTTP_AUTHORIZATION=AUTH,
        )
        self.assertEqual(resp.status_code, 201)
        resp2 = self.client.put(
            url, json.dumps({"title": "Up2", "content": "<p>b</p>", "excerpt": "y"}),
            content_type="application/json", HTTP_AUTHORIZATION=AUTH,
        )
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(BlogPost.objects.get(slug="upsert-me").title, "Up2")

    def test_put_slug_mismatch_is_400(self):
        resp = self.client.put(
            self._detail("a"),
            json.dumps({"title": "T", "content": "<p>a</p>", "excerpt": "x",
                        "slug": "b"}),
            content_type="application/json", HTTP_AUTHORIZATION=AUTH,
        )
        self.assertEqual(resp.status_code, 400)

    def test_patch_partial_update(self):
        self._post({"title": "P", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "p"})
        resp = self.client.patch(
            self._detail("p"), json.dumps({"title": "Patched"}),
            content_type="application/json", HTTP_AUTHORIZATION=AUTH,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(BlogPost.objects.get(slug="p").title, "Patched")

    def test_patch_slug_change_rejected(self):
        self._post({"title": "P", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "keep"})
        resp = self.client.patch(
            self._detail("keep"), json.dumps({"slug": "changed"}),
            content_type="application/json", HTTP_AUTHORIZATION=AUTH,
        )
        self.assertEqual(resp.status_code, 400)

    def test_patch_missing_is_404(self):
        resp = self.client.patch(
            self._detail("ghost"), json.dumps({"title": "x"}),
            content_type="application/json", HTTP_AUTHORIZATION=AUTH,
        )
        self.assertEqual(resp.status_code, 404)

    # --- delete ---
    def test_delete_returns_204(self):
        self._post({"title": "Del", "content": "<p>a</p>", "excerpt": "x",
                    "slug": "del"})
        resp = self.client.delete(self._detail("del"), HTTP_AUTHORIZATION=AUTH)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(BlogPost.objects.filter(slug="del").exists())

    def test_delete_missing_is_404(self):
        resp = self.client.delete(self._detail("ghost"), HTTP_AUTHORIZATION=AUTH)
        self.assertEqual(resp.status_code, 404)
