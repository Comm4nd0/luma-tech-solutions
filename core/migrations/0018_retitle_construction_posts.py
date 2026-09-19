"""Sharpen the titles of the two construction blog posts.

Search Console (Aug–Sep 2026) had both posts on page one — around position 9
for construction-site CCTV and ANPR/ICO queries — with a combined 60+
impressions and zero clicks. The titles named the topic but gave no reason
to click. The 0015 seed migration is already applied in production, so the
new titles have to land as a data migration. Slugs are untouched, so no URL
changes and no redirects.

Idempotent — a second run finds the new titles already in place and no-ops.
"""
from django.db import migrations


# {slug: {field: new_value}}
UPDATES = {
    "construction-site-cctv-hire-vs-buy": {
        "title": "Construction Site CCTV Hire vs Buy: What Each Really Costs",
        "meta_description": (
            "Hire or buy site CCTV? What hire really costs over a build "
            "programme, when installed cameras with gate ANPR pay for "
            "themselves, and when hire still wins."
        ),
    },
    "anpr-building-sites-ico-obligations": {
        "title": "ANPR on Building Sites: 5 ICO Rules You Must Follow",
        "meta_description": (
            "Running ANPR on a building site? The five things the ICO "
            "expects: registration, DPIA, signage, retention and who does "
            "the paperwork. Plain English for UK builders."
        ),
    },
}


def retitle_posts(apps, schema_editor):
    BlogPost = apps.get_model("core", "BlogPost")
    for slug, fields in UPDATES.items():
        BlogPost.objects.filter(slug=slug).update(**fields)


def noop_reverse(apps, schema_editor):
    # Forward-only: the old titles were the ones losing the clicks.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_smart_home_choice_labels"),
    ]

    operations = [
        migrations.RunPython(retitle_posts, reverse_code=noop_reverse),
    ]
