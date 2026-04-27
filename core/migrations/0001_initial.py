from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContactSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                (
                    "service",
                    models.CharField(
                        choices=[
                            ("networking", "Wi-Fi & Networking"),
                            ("development", "App & Web Development"),
                            ("automation", "Home Automation"),
                            ("support", "Support & Maintenance"),
                            ("other", "Something else"),
                        ],
                        default="other",
                        max_length=32,
                    ),
                ),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("notified", models.BooleanField(default=False)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
