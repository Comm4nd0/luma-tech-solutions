"""Care-plan data did not change when the two lists were merged.

The literals below are the pre-refactor HOME_CARE_PLANS and
BUSINESS_CARE_PLANS, pasted verbatim. They are a proof that
care_plans() reproduces them exactly, and a standing guard on pricing
and SLA copy: if a tier's price or feature list changes, this test says so.
"""

from django.test import SimpleTestCase

from core.content import care_plans

_OLD_HOME = [{'name': 'Essential',
  'price': '£75',
  'price_suffix': '/mo +VAT',
  'annual_price': '£810',
  'annual_suffix': '/yr',
  'min_term': '3-month rolling',
  'tagline': 'Quiet, reliable IT — we watch it, you forget about it.',
  'highlighted': False,
  'features': ['24/7 automated network monitoring with alerts to us',
               'Firmware, security patches and daily config backups managed for you',
               'Email support — next business day for routine, same business day (best effort) for '
               'service-down',
               'Quarterly health-check report',
               'One-page network diagram, kept current with any changes we make',
               '20% off our standard hourly rate for work outside the plan',
               'Internet provider liaison when your line goes down — we make the calls']},
 {'name': 'Professional',
  'price': '£165',
  'price_suffix': '/mo +VAT',
  'annual_price': '£1,780',
  'annual_suffix': '/yr',
  'min_term': '6-month rolling',
  'tagline': 'Hands-on support for everything Luma installed — same engineer who built it.',
  'highlighted': True,
  'features': ['Everything in Essential',
               'Reactive support for any kit, app or integration we supplied or installed — '
               'networking, CCTV, smart-home, custom apps',
               'Same business day for routine; target within 4 working hours for service-down',
               'Phone, video and WhatsApp support',
               '2 hours of remote moves-and-changes per year (rolls over up to 4)',
               'One on-site visit per year included (tune-up, cable check, hardware audit)',
               'Warranty management on hardware we supply — UI Care registered, RMAs handled by us',
               '5% loyalty discount from year 2']},
 {'name': 'Concierge',
  'price': '£325',
  'price_suffix': '/mo +VAT',
  'annual_price': '£3,510',
  'annual_suffix': '/yr',
  'min_term': '12-month',
  'tagline': 'The whole smart home, whoever installed it — one engineer, one number, one bill.',
  'highlighted': False,
  'features': ['Everything in Professional',
               "We'll take a look at any smart-home product in the house, whoever installed it — "
               'Lutron, Ring, Nest, Hue, legacy integrations. Diagnose, advise and escalate '
               "to the manufacturer; we don't warrant kit we didn't supply, but you've got one "
               'number to call.',
               'Front of queue; target within 2 working hours for service-down',
               'Best-effort out-of-hours for genuine emergencies',
               'One on-site visit per quarter + monthly check-in call',
               '6 hours of remote moves-and-changes per year (rolls over up to 12)',
               'Full living documentation — network map, device inventory, credentials vault, '
               'runbook',
               'Loaner hardware where we have stock; otherwise we expedite the RMA on your behalf',
               'Multi-site coverage — main home plus a holiday let or small office under one plan',
               '10% loyalty discount from year 2']}]

_OLD_BUSINESS = [{'name': 'Essential',
  'price': '£25',
  'price_suffix': '/user/mo +VAT',
  'annual_price': '£270',
  'annual_suffix': '/user/yr',
  'min_term': '3-month rolling',
  'tagline': 'Quiet, reliable IT for small teams — we watch it, you focus on the work.',
  'highlighted': False,
  'features': ['24/7 automated network monitoring with alerts to us',
               'Firmware, security patches and daily config backups managed for you',
               'Email support — next business day for routine, same business day (best effort) for '
               'service-down',
               'Quarterly health-check report',
               'One-page network diagram, kept current with any changes we make',
               '20% off our standard hourly rate for work outside the plan',
               'Internet provider liaison when your line goes down — we make the calls']},
 {'name': 'Professional',
  'price': '£55',
  'price_suffix': '/user/mo +VAT',
  'annual_price': '£595',
  'annual_suffix': '/user/yr',
  'min_term': '6-month rolling',
  'tagline': 'Hands-on support for everything Luma installed — same engineer who built it.',
  'highlighted': True,
  'features': ['Everything in Essential',
               'Reactive support for any kit, app or integration we supplied or installed — '
               'networking, CCTV, point-of-sale, custom apps',
               'Same business day for routine; target within 4 working hours for service-down',
               'Phone, video and WhatsApp support',
               '2 hours of remote moves-and-changes per user per year (rolls over up to 4)',
               'One on-site visit per quarter (cable check, hardware audit, team Q&A)',
               'Warranty management on hardware we supply — UI Care registered, RMAs handled by us',
               '5% loyalty discount from year 2']},
 {'name': 'Concierge',
  'price': '£110',
  'price_suffix': '/user/mo +VAT',
  'annual_price': '£1,190',
  'annual_suffix': '/user/yr',
  'min_term': '12-month',
  'tagline': 'The whole office, whoever installed it — one engineer, one number, one bill.',
  'highlighted': False,
  'features': ['Everything in Professional',
               "We'll take a look at any networked product on the premises, whoever installed it — "
               'printers, NAS, VOIP, point-of-sale, legacy kit from a previous IT company. '
               "Diagnose, advise and escalate to the manufacturer; we don't warrant kit we didn't "
               "supply, but you've got one number to call.",
               'Front of queue; target within 2 working hours for service-down',
               'Best-effort out-of-hours for genuine emergencies',
               'One on-site visit per month + monthly check-in call',
               '6 hours of remote moves-and-changes per user per year (rolls over up to 12)',
               'Full living documentation — network map, device inventory, credentials vault, '
               'runbook',
               'Loaner hardware where we have stock; otherwise we expedite the RMA on your behalf',
               'Multi-site coverage — main office plus a satellite or warehouse under one plan',
               '10% loyalty discount from year 2']}]


def _without_key(plans):
    """care_plans() adds a "key" field the old literals had no equivalent for;
    every other field must match byte for byte."""
    return [{k: v for k, v in p.items() if k != "key"} for p in plans]


class CarePlanEquivalenceTests(SimpleTestCase):
    def test_home_plans_unchanged(self):
        self.assertEqual(_without_key(care_plans("home")), _OLD_HOME)

    def test_business_plans_unchanged(self):
        self.assertEqual(_without_key(care_plans("business")), _OLD_BUSINESS)

    def test_every_plan_carries_its_tier_key(self):
        # support.html builds the ?plan= link from this, and the contact view
        # resolves it back through CARE_TIERS.
        for audience in ("home", "business"):
            with self.subTest(audience=audience):
                self.assertEqual(
                    [p["key"] for p in care_plans(audience)],
                    ["essential", "professional", "concierge"],
                )

    def test_tier_order_is_stable(self):
        # The support page renders the grid in list order.
        for audience in ("home", "business"):
            with self.subTest(audience=audience):
                self.assertEqual(
                    [p["name"] for p in care_plans(audience)],
                    ["Essential", "Professional", "Concierge"],
                )
