from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.forms import QuoteRequestForm
from core.models import ContactSubmission, QuoteRequest


@override_settings(RECAPTCHA_SECRET_KEY='', EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ResidentialEnquiryTests(TestCase):
    def test_minimal_quote_saves_without_property_budget_or_timing(self):
        response = self.client.post(reverse('quote'), {
            'name': 'Homeowner', 'email': 'home@example.com',
            'postcode': 'sl7 1aa', 'services': ['networking'],
            'stage': 'won', 'project_value': '99999', 'care_plan': 'concierge',
        })
        self.assertRedirects(response, reverse('quote_thanks'))
        lead = QuoteRequest.objects.get()
        self.assertEqual(lead.property_type, 'home_unsure')
        self.assertEqual(lead.postcode, 'SL7 1AA')
        self.assertEqual(lead.stage, 'new')
        self.assertIsNone(lead.project_value)
        self.assertEqual(lead.care_plan, '')

    def test_security_contact_is_prefilled_and_accepted(self):
        response = self.client.get(reverse('contact') + '?service=security')
        self.assertEqual(response.context['form'].initial['service'], 'security')
        response = self.client.post(reverse('contact'), {
            'name': 'Homeowner', 'email': 'home@example.com',
            'service': 'security', 'message': 'Cameras for the drive',
            'referral': 'Our electrician', 'source': 'cctv-sidebar',
            'utm_source': 'google', 'utm_medium': 'cpc', 'utm_campaign': 'home-cctv',
        })
        self.assertRedirects(response, reverse('contact_thanks'))
        lead = ContactSubmission.objects.get()
        self.assertEqual(lead.service, 'security')
        self.assertEqual(lead.referral, 'Our electrician')
        self.assertEqual(lead.utm_campaign, 'home-cctv')

    def test_optional_details_and_trade_services_reopen_on_errors(self):
        response = self.client.post(reverse('quote'), {
            'name': 'Homeowner', 'services': ['site_security'], 'property_type': 'bad',
        })
        self.assertContains(response, 'class="form-details" open')
        self.assertIn('property_type', response.context['form'].errors)
        self.assertRegex(response.content.decode(), r'<input(?=[^>]*value="site_security")(?=[^>]*checked)[^>]*>')

    def test_construction_link_opens_prefilled_sections(self):
        response = self.client.get(reverse('quote') + '?service=site_security,%20prewire&property=construction_site')
        self.assertTrue(response.context['show_other_services'])
        self.assertTrue(response.context['show_project_details'])
        self.assertEqual(response.context['form'].initial['services'], ['site_security', 'prewire'])

    def test_campaign_tags_are_bounded_and_unrelated_parameters_ignored(self):
        response = self.client.get(reverse('quote'), {'utm_source': 'a' * 150, 'source': 'b' * 100, 'email': 'private@example.com'})
        initial = response.context['form'].initial
        self.assertEqual(len(initial['utm_source']), 100)
        self.assertEqual(len(initial['source']), 64)
        self.assertNotIn('email', initial)

    def test_conversion_requires_saved_submission_and_is_not_replayed(self):
        for kind in ('quote', 'contact'):
            with self.subTest(kind=kind):
                thanks = reverse(kind + '_thanks')
                self.assertNotContains(self.client.get(thanks), "gtag('event', 'conversion'")
                invalid = self.client.post(reverse(kind), {})
                self.assertEqual(invalid.status_code, 200)
                self.assertNotContains(self.client.get(thanks), 'Enquiry received')
                values = {'name': 'Private Name', 'email': 'private@example.com'}
                if kind == 'quote':
                    values.update(postcode='SL7 1AA', services=['networking'])
                else:
                    values.update(service='security', message='Private message')
                self.client.post(reverse(kind), values)
                response = self.client.get(thanks)
                self.assertContains(response, 'Enquiry received')
                self.assertContains(response, "'transaction_id'")
                self.assertNotContains(response, 'private@example.com')
                self.assertNotContains(response, 'Private message')
                self.assertNotContains(self.client.get(thanks), 'Enquiry received')

    def test_quote_errors_have_existing_accessible_descriptions(self):
        import re
        html = self.client.post(reverse('quote'), {}).content.decode()
        for description in re.findall(r'aria-describedby="([^"]+)"', html):
            for token in description.split():
                self.assertIn('id="' + token + '"', html)


class EnquiryAdminTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser('owner', 'owner@example.com', 'test-password')
        self.client.force_login(user)
        self.lead = QuoteRequest.objects.create(name='Test', email='test@example.com', postcode='SL7 1AA', services='networking,security')
        self.admin = admin.site._registry[QuoteRequest]

    def test_installation_sets_followup_once_and_respects_manual_date(self):
        self.lead.stage = 'installed'
        self.admin.save_model(None, self.lead, Mock(changed_data=['stage']), True)
        today = timezone.localdate()
        self.assertEqual(self.lead.installed_on, today)
        self.assertEqual(self.lead.follow_up_on, today + timedelta(days=14))
        self.lead.follow_up_on = today + timedelta(days=5)
        self.admin.save_model(None, self.lead, Mock(changed_data=['follow_up_on']), True)
        self.assertEqual(self.lead.follow_up_on, today + timedelta(days=5))
        self.lead.follow_up_on = today + timedelta(days=7)
        self.admin.save_model(None, self.lead, Mock(changed_data=['stage', 'follow_up_on']), True)
        self.assertEqual(self.lead.follow_up_on, today + timedelta(days=7))

    def test_summary_uses_filters_and_only_known_accepted_values(self):
        self.lead.stage = 'won'
        self.lead.project_value = Decimal('1000')
        self.lead.direct_cost = Decimal('700')
        self.lead.save()
        QuoteRequest.objects.create(name='Other', email='other@example.com', postcode='SL7 1AA', services='automation', stage='lost', project_value=9999)
        response = self.client.get(reverse('admin:core_quoterequest_changelist'))
        summary = response.context['lead_summary']
        self.assertEqual(summary['enquiries'], 2)
        self.assertEqual(summary['accepted'], 1)
        self.assertEqual(summary['revenue'], Decimal('1000'))
        self.assertEqual(summary['margin'], Decimal('300'))
        filtered = self.client.get(reverse('admin:core_quoterequest_changelist'), {'service': 'security'})
        self.assertEqual(filtered.context['lead_summary']['enquiries'], 1)

    def test_due_filter_excludes_closed_enquiries(self):
        self.lead.follow_up_on = timezone.localdate() - timedelta(days=1)
        self.lead.save()
        response = self.client.get(reverse('admin:core_quoterequest_changelist'), {'follow_up': 'due'})
        self.assertEqual(response.context['lead_summary']['enquiries'], 1)
        self.lead.stage = 'lost'
        self.lead.save()
        response = self.client.get(reverse('admin:core_quoterequest_changelist'), {'follow_up': 'due'})
        self.assertEqual(response.context['lead_summary']['enquiries'], 0)

    def test_negative_costs_are_rejected(self):
        self.lead.direct_cost = -1
        with self.assertRaises(ValidationError):
            self.lead.full_clean()

    def test_outreach_drafts_render_but_do_not_send_mail(self):
        from django.core import mail
        response = self.client.get(reverse('admin:core_quoterequest_change', args=[self.lead.pk]))
        self.assertContains(response, 'No messages are sent automatically.')
        self.assertContains(response, 'review-draft')
        self.assertEqual(len(mail.outbox), 0)

    def test_staff_without_model_permission_cannot_see_pipeline(self):
        user = get_user_model().objects.create_user('limited', is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('admin:core_quoterequest_changelist')).status_code, 403)


from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class EnquiryMigrationTests(TransactionTestCase):
    def test_existing_leads_survive_and_previous_app_can_still_insert(self):
        before = [('core', '0018_retitle_construction_posts')]
        after = [('core', '0019_residential_enquiry_workflow')]
        executor = MigrationExecutor(connection)
        try:
            executor.migrate(before)
            old_apps = executor.loader.project_state(before).apps
            OldContact = old_apps.get_model('core', 'ContactSubmission')
            OldQuote = old_apps.get_model('core', 'QuoteRequest')
            contact = OldContact.objects.create(name='Existing contact', email='existing@example.com', message='Keep this enquiry', source='original-source')
            quote = OldQuote.objects.create(name='Existing quote', email='existing@example.com', postcode='SL7 1AA', services='networking', notes='Keep these notes')
            executor = MigrationExecutor(connection)
            executor.migrate(after)
            self.assertEqual(ContactSubmission.objects.get(pk=contact.pk).message, 'Keep this enquiry')
            self.assertEqual(ContactSubmission.objects.get(pk=contact.pk).source, 'original-source')
            self.assertEqual(QuoteRequest.objects.get(pk=quote.pk).notes, 'Keep these notes')
            self.assertEqual(QuoteRequest.objects.get(pk=quote.pk).stage, 'new')
            # Automatic code rollback must not stop the older model inserting leads.
            new_contact = OldContact.objects.create(name='Rollback contact', email='rollback@example.com', message='New enquiry')
            new_quote = OldQuote.objects.create(name='Rollback quote', email='rollback@example.com', postcode='SL7 1AA')
            self.assertEqual(ContactSubmission.objects.get(pk=new_contact.pk).stage, 'new')
            self.assertEqual(QuoteRequest.objects.get(pk=new_quote.pk).utm_source, '')
        finally:
            MigrationExecutor(connection).migrate(after)
