"""Remove smart-lock content from the live database.

We never installed smart locks, so the dedicated 2026-07-14 blog post and a
passing mention inside the Royal Marines post need to come off the live site.
The 0003 seed migration is already applied in production, so editing the
seeded content there alone won't update live records — this data migration
deletes the dedicated post and patches the other.

Idempotent — second run finds nothing to delete or replace and no-ops.
"""
from django.db import migrations


POST_SLUG_TO_DELETE = "smart-locks-are-they-actually-secure"

# {slug: {field_name: [(old, new), ...]}}
REPLACEMENTS = {
    "what-the-royal-marines-taught-me-about-reliable-networks": {
        "content": [
            (
                "Every UniFi access point. Every Home Assistant integration. Every smart lock. If we wouldn't trust it for our own family, it doesn't get on a quote.",
                "Every UniFi access point. Every Home Assistant integration. Every camera. If we wouldn't trust it for our own family, it doesn't get on a quote.",
            ),
        ],
    },
}


def remove_smart_lock_content(apps, schema_editor):
    BlogPost = apps.get_model("core", "BlogPost")
    BlogPost.objects.filter(slug=POST_SLUG_TO_DELETE).delete()
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
    # Forward-only: we don't want to bring smart-lock copy back.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_quoterequest"),
    ]

    operations = [
        migrations.RunPython(remove_smart_lock_content, reverse_code=noop_reverse),
    ]
