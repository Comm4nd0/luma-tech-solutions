"""Drop "enterprise" wording from the three blog posts that mention it.

We're not targeting enterprise companies — large homes and small/medium
businesses only. The 0003 seed migration has been edited so future fresh
installs are clean; this data migration applies the same find/replace to
existing rows in the live DB.

The three posts are all scheduled-future at deploy time (May/Jun/Jul 2026),
but we update them now so they go live with the corrected wording when
their published_at falls due.

Idempotent — second run finds no matches and no-ops.
"""
from django.db import migrations


REPLACEMENTS = {
    "complete-guide-to-unifi-for-homes": {
        "content": [
            (
                'friendlier than most enterprise gear',
                'friendlier than most pro-grade kit',
            ),
        ],
    },
    "why-your-tech-needs-a-support-plan": {
        "content": [
            (
                "<li><strong>Enterprise — £149/month.</strong> Priority response, monthly check-in, quarterly on-site visit, full documentation kept up to date. Right for businesses or larger residential installs.</li>",
                "<li><strong>Concierge — £149/month.</strong> Priority response, monthly check-in, quarterly on-site visit, full documentation kept up to date. Right for businesses or larger residential installs.</li>",
            ),
        ],
    },
    "smart-locks-are-they-actually-secure": {
        "content": [
            (
                "Audit trail and integration is enterprise-grade.",
                "Audit trail and integration is professional-grade.",
            ),
        ],
    },
}


def remove_enterprise_references(apps, schema_editor):
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
    # Forward-only: we don't want to put the enterprise wording back.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_remove_drone_references"),
    ]

    operations = [
        migrations.RunPython(remove_enterprise_references, reverse_code=noop_reverse),
    ]
