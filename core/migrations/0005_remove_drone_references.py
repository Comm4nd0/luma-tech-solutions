"""Rewrite the three blog posts that mention drone/aerial surveys.

The 0003 seed migration is already applied in production, so editing the
seeded content there alone won't update live records. This data migration
performs the same find-and-replace operations against any existing rows.

Idempotent — second run finds no matches and no-ops.
"""
from django.db import migrations


# {slug: {field_name: [(old, new), ...]}}
REPLACEMENTS = {
    "why-your-home-wifi-isnt-as-good-as-it-could-be": {
        "content": [
            (
                'We fly a drone survey before drilling, because the obvious spot is surprisingly often the wrong spot.',
                'We do a thorough on-site survey before drilling, because the obvious spot is surprisingly often the wrong spot.',
            ),
            (
                "We'll walk the property, fly a drone survey and tell you honestly whether it's a £200 fix or a proper rebuild.",
                "We'll walk the property, do a proper on-site survey and tell you honestly whether it's a £200 fix or a proper rebuild.",
            ),
        ],
    },
    "complete-guide-to-unifi-for-homes": {
        "content": [
            (
                "Drone survey, written quote, fixed price.",
                "On-site survey, written quote, fixed price.",
            ),
        ],
    },
    "home-cctv-camera-placement-tips": {
        "content": [
            (
                "<h2>The drone survey</h2>\n"
                "<p>Once we've got rough zones, we fly an aerial drone survey before drilling anything. "
                "Two reasons. First, it surfaces blind spots you can't see from the ground — roof angles, "
                "overhanging trees that hide an approach, neighbouring sight-lines. Second, it lets us "
                "pre-plan cable routes and PoE distances. By the time install day comes round, we know "
                "exactly where every camera goes and how the cable runs.</p>\n"
                "<p>The aerial imagery is handed over to you with the runbook — useful for insurance, "
                "useful if we ever expand the system, useful as a record of the property as it was.</p>",
                "<h2>Plan it on paper before drilling</h2>\n"
                "<p>Once we've got rough zones, we walk the property top-to-bottom and sketch the install "
                "before drilling anything. We measure cable runs, check sight-lines from each proposed "
                "camera position, and identify blind spots from ground level — the sort of thing that's "
                "easy to miss until day-of-install. By the time install day comes round, we know exactly "
                "where every camera goes and how the cable runs.</p>\n"
                "<p>A written placement plan is handed over to you with the runbook — useful for insurance, "
                "useful if we ever expand the system, useful as a record of the property as it was.</p>",
            ),
            (
                "we'll walk the property, fly the drone, talk you through the zones",
                "we'll walk the property, talk you through the zones",
            ),
        ],
        "excerpt": [
            (
                "Coverage zones, height, angle, sun, night vision and the drone survey — how we plan CCTV installs across Berks and Bucks.",
                "Coverage zones, height, angle, sun and night vision — how we plan CCTV installs that actually catch what matters.",
            ),
        ],
        "meta_description": [
            (
                "How to plan home CCTV that actually catches what matters: coverage zones, height, angles, sun, night vision and aerial surveys.",
                "How to plan home CCTV that actually catches what matters: coverage zones, height, angles, sun and night vision.",
            ),
        ],
    },
}


def remove_drone_references(apps, schema_editor):
    BlogPost = apps.get_model("core", "BlogPost")
    for slug, fields in REPLACEMENTS.items():
        try:
            post = BlogPost.objects.get(slug=slug)
        except BlogPost.DoesNotExist:
            continue
        changed = False
        for fname, pairs in fields.items():
            value = getattr(post, fname)
            for old, new in pairs:
                if old in value:
                    value = value.replace(old, new)
                    changed = True
            setattr(post, fname, value)
        if changed:
            post.save()


def noop_reverse(apps, schema_editor):
    # Forward-only: we don't want to put drone copy back.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_contactsubmission_source"),
    ]

    operations = [
        migrations.RunPython(remove_drone_references, reverse_code=noop_reverse),
    ]
