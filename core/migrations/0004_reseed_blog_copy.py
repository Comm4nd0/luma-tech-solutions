"""Re-apply the blog seed so copy edits in 0003 reach already-seeded databases.

Migration 0003 only runs once, so editing its content constants updates fresh
installs but not existing production data. This migration re-invokes 0003's
`seed_posts`, which uses `update_or_create` keyed on slug — updating the
content / excerpt / meta_description of the existing rows in place.
"""
import importlib

from django.db import migrations


# 0003's module name starts with a digit, so a normal import won't work.
_seed = importlib.import_module("core.migrations.0003_seed_blog_posts")


def reseed(apps, schema_editor):
    _seed.seed_posts(apps, schema_editor)


def noop(apps, schema_editor):
    # Nothing to undo — the rows are managed by 0003's reverse op.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_seed_blog_posts"),
    ]

    operations = [
        migrations.RunPython(reseed, reverse_code=noop),
    ]
