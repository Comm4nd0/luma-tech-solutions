import re

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import BlogPost


# Strip any pre-existing image references that point at our static asset
# trees — older drafts of these posts shipped with placeholder image tags
# that we want gone before we splice in the new illustrations.
STALE_IMG_RE = re.compile(
    r'<img\b[^>]*\bsrc="/static/img/(?:blog|services)/[^"]*"[^>]*>\s*',
    re.IGNORECASE,
)


def img_tag(filename: str, alt: str) -> str:
    return (
        f'<img src="/static/img/blog/{filename}" alt="{alt}" '
        f'loading="lazy" width="1200" height="630">'
    )


# Each entry: post id → list of (section, <img> tag). The "section"
# is 1-based and matches the user-visible section ordering: section 1
# is the first <h2>, section 3 is the third <h2>, etc. The image is
# inserted immediately before that <h2>, after any preceding intro or
# section content.
POST_UPDATES = {
    18: [
        (
            1,
            img_tag(
                "it-maintenance-router.svg",
                "Business router with status LEDs flagging a fault — "
                "the kind of warning sign our IT maintenance team in "
                "Thames Valley spots before it becomes downtime.",
            ),
        ),
        (
            3,
            img_tag(
                "it-maintenance-backup.svg",
                "Backup shield protecting business storage drives — "
                "tested, off-site backups for SMEs across Berkshire "
                "and Buckinghamshire.",
            ),
        ),
        (
            4,
            img_tag(
                "it-maintenance-cables.svg",
                "Tangled cabling on the left, tidy patching on the "
                "right — structured cabling tidy-ups for offices in "
                "Marlow, Maidenhead and Henley.",
            ),
        ),
    ],
    17: [
        (
            1,
            img_tag(
                "website-responsive.svg",
                "Same small business website rendered on desktop and "
                "mobile — responsive web design for companies across "
                "the Thames Valley.",
            ),
        ),
        (
            4,
            img_tag(
                "website-seo.svg",
                "Magnifying glass over local search results with an "
                "upward trend — local SEO for small businesses in "
                "Berkshire and Buckinghamshire.",
            ),
        ),
    ],
    15: [
        (
            1,
            img_tag(
                "automation-hub.svg",
                "Central smart home hub connecting lighting, heating "
                "and security devices — home automation installs in "
                "Marlow, Maidenhead and Henley.",
            ),
        ),
        (
            4,
            img_tag(
                "automation-voice.svg",
                "Voice-controlled smart speaker inside a home with a "
                "privacy padlock — secure home automation across the "
                "Thames Valley.",
            ),
        ),
    ],
    1: [
        (
            1,
            img_tag(
                "wifi-signal.svg",
                "Cross-section of a Thames Valley home showing a "
                "Wi-Fi signal weakening as it passes through internal "
                "walls.",
            ),
        ),
        (
            4,
            img_tag(
                "wifi-access-points.svg",
                "Floor plan with three ceiling access points giving "
                "overlapping Wi-Fi coverage — whole-home Wi-Fi "
                "installs in Berkshire and Buckinghamshire.",
            ),
        ),
    ],
}


def splice_images(content: str, inserts: list[tuple[int, str]]) -> str:
    """Insert image tags before the Nth <h2> section heading.

    Splits content on a <h2> lookahead so each chunk begins with its
    <h2>; chunk 1 is section 1, chunk N is section N. Prepending to
    chunk N puts the image immediately before section N's <h2>.
    """
    parts = re.split(r"(?i)(?=<h2\b)", content)
    if not parts:
        return content

    # Group inserts by section, preserving the order they were declared.
    grouped: dict[int, list[str]] = {}
    for idx, tag in inserts:
        grouped.setdefault(idx, []).append(tag)

    for idx in sorted(grouped.keys(), reverse=True):
        if idx < 0 or idx >= len(parts):
            continue
        injected = "".join(t + "\n" for t in grouped[idx])
        parts[idx] = injected + parts[idx]

    return "".join(parts)


class Command(BaseCommand):
    help = "Insert SEO-optimised SVG illustrations into specific blog posts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        with transaction.atomic():
            for post_id, inserts in POST_UPDATES.items():
                try:
                    post = BlogPost.objects.get(pk=post_id)
                except BlogPost.DoesNotExist:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Skipping post id={post_id}: not found."
                        )
                    )
                    continue

                original = post.content or ""
                cleaned, removed = STALE_IMG_RE.subn("", original)
                updated = splice_images(cleaned, inserts)

                if updated == original:
                    self.stdout.write(
                        f"id={post_id} '{post.title}': no change."
                    )
                    continue

                self.stdout.write(
                    f"id={post_id} '{post.title}': "
                    f"removed {removed} stale image(s), "
                    f"inserted {len(inserts)} new image(s)."
                )

                if not dry_run:
                    post.content = updated
                    post.save(update_fields=["content", "updated_at"])

            if dry_run:
                self.stdout.write(self.style.NOTICE("Dry run — rolling back."))
                transaction.set_rollback(True)
            else:
                self.stdout.write(self.style.SUCCESS("Done."))
