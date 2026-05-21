"""One-shot management command to rewrite externally hosted blog imagery
to locally hosted copies under ``/static/img/blog/``.

We previously embedded a handful of Marblism CDN URLs in two blog posts
(Gigabit Wi-Fi and the CCTV Subscription article). Relying on a
third-party CDN means our blog visuals break if Marblism goes away — so
this command rewrites those URLs to the local copies that now ship in
``static/img/blog/`` and tightens up some of the auto-generated alt text
along the way.

The command is idempotent — it scans every BlogPost (drafts included),
finds any URL listed in ``URL_MAP`` in the post body, and rewrites in
place. Running it twice is a no-op.

Usage:

    docker compose exec web python manage.py rewrite_external_blog_images
"""

import re

from django.core.management.base import BaseCommand

from core.models import BlogPost


# Marblism CDN URL → local /static/img/blog/<file>.webp.
# The image files live under static/img/blog/ in the repo.
URL_MAP = {
    "https://cdn.marblism.com/ZFoGivXOfzT.webp": "/static/img/blog/gigabit-wifi-hero.webp",
    "https://cdn.marblism.com/dUq25cYtZF0.webp": "/static/img/blog/gigabit-wifi-2.webp",
    "https://cdn.marblism.com/UzHho8Wfo_v.webp": "/static/img/blog/gigabit-wifi-3.webp",
    "https://cdn.marblism.com/5fAnTfxkp9E.webp": "/static/img/blog/gigabit-wifi-4.webp",
    "https://cdn.marblism.com/jAf9nj50xtX.webp": "/static/img/blog/cctv-subscription-hero.webp",
    "https://cdn.marblism.com/tb5_BuojeuK.webp": "/static/img/blog/cctv-subscription-2.webp",
    "https://cdn.marblism.com/_VNIAuTomwA.webp": "/static/img/blog/cctv-subscription-3.webp",
    "https://cdn.marblism.com/bYOaSpdOlge.webp": "/static/img/blog/cctv-subscription-4.webp",
    "https://cdn.marblism.com/qwh_9kUv81q.webp": "/static/img/blog/cctv-subscription-5.webp",
}


# Alt-text replacements for known-bad alt values that came out of the
# original image-generation tool ("heroImage" being the obvious one).
# Per-slug so we can give each post a sensible, keyword-rich alt.
ALT_REPLACEMENTS = {
    "paying-for-gigabit-5-reasons-your-home-wi-fi-still-feels-slow-and-how-to-fix-it": {
        "heroImage": (
            "Home Wi-Fi router on a desk — gigabit broadband doesn't mean "
            "fast Wi-Fi"
        ),
    },
}


class Command(BaseCommand):
    help = "Rewrite external (Marblism) blog image URLs to local /static/img/blog/ copies."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving.",
        )

    def handle(self, *args, **opts):
        dry = opts["dry_run"]
        total_url_rewrites = 0
        total_alt_rewrites = 0
        posts_touched = 0

        for post in BlogPost.objects.all():
            original = post.content or ""
            updated = original

            # URL rewrites.
            url_hits = 0
            for old, new in URL_MAP.items():
                count = updated.count(old)
                if count:
                    updated = updated.replace(old, new)
                    url_hits += count

            # Alt-text rewrites (per-slug).
            alt_hits = 0
            for bad_alt, good_alt in ALT_REPLACEMENTS.get(post.slug, {}).items():
                # Match `alt="heroImage"` or `alt='heroImage'` only — don't
                # accidentally rewrite the word inside the article body.
                pattern = re.compile(
                    r'(alt\s*=\s*["\']\s*)' + re.escape(bad_alt) + r'(\s*["\'])'
                )
                new_value, n = pattern.subn(rf'\g<1>{good_alt}\g<2>', updated)
                if n:
                    updated = new_value
                    alt_hits += n

            if updated == original:
                continue

            posts_touched += 1
            total_url_rewrites += url_hits
            total_alt_rewrites += alt_hits

            self.stdout.write(
                f"{post.slug}: {url_hits} url(s), {alt_hits} alt(s){' [dry]' if dry else ''}"
            )

            if not dry:
                post.content = updated
                post.save(update_fields=["content", "updated_at"])

        summary = (
            f"Posts touched: {posts_touched}. "
            f"URL rewrites: {total_url_rewrites}. "
            f"Alt rewrites: {total_alt_rewrites}."
        )
        self.stdout.write(self.style.SUCCESS(summary if not dry else f"[DRY RUN] {summary}"))
