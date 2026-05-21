# Hand-written migration for the new QuoteRequest model.
#
# Adds a dedicated table for structured quote enquiries from the new
# `/quote/` landing page. Kept separate from ContactSubmission so we can
# report on the dedicated quote funnel independently.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_alter_jobapplication_role'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=40)),
                ('postcode', models.CharField(
                    help_text='UK postcode — used to confirm the property is in our coverage area.',
                    max_length=16,
                )),
                ('property_type', models.CharField(
                    choices=[
                        ('home_small', 'Home — under 150 m²'),
                        ('home_medium', 'Home — 150–300 m²'),
                        ('home_large', 'Home — 300 m² or larger'),
                        ('home_period', 'Period or listed home'),
                        ('home_estate', 'Estate or multi-building property'),
                        ('business_office', 'Business — office'),
                        ('business_retail', 'Business — retail / hospitality'),
                        ('business_other', 'Business — something else'),
                        ('other', 'Something else'),
                    ],
                    default='other',
                    max_length=32,
                )),
                ('services', models.CharField(
                    blank=True,
                    default='',
                    help_text="Comma-separated service keys, e.g. 'networking,security'.",
                    max_length=200,
                )),
                ('timeline', models.CharField(
                    blank=True,
                    choices=[
                        ('urgent', 'Within 2 weeks'),
                        ('soon', 'Within the next month'),
                        ('planned', '1–3 months'),
                        ('flexible', 'Flexible / just exploring'),
                    ],
                    default='',
                    max_length=16,
                )),
                ('budget', models.CharField(
                    blank=True,
                    choices=[
                        ('under_2k', 'Under £2,000'),
                        ('2k_5k', '£2,000 – £5,000'),
                        ('5k_15k', '£5,000 – £15,000'),
                        ('15k_50k', '£15,000 – £50,000'),
                        ('50k_plus', '£50,000+'),
                        ('not_sure', 'Not sure yet'),
                    ],
                    default='',
                    max_length=16,
                )),
                ('notes', models.TextField(blank=True)),
                ('source', models.CharField(
                    blank=True,
                    default='',
                    help_text='Internal tag identifying which page/CTA the enquiry came from.',
                    max_length=64,
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notified', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
