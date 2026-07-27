"""Accessibility guarantees that are cheap to regress silently."""

import re

from django.test import TestCase
from django.urls import reverse


class SkipLinkTests(TestCase):
    def test_skip_link_is_not_pinned_offscreen_inline(self):
        # It used to carry style="position:absolute;left:-9999px;" inline with
        # no matching CSS rule, so nothing could ever reveal it on focus.
        resp = self.client.get(reverse("home"))
        html = resp.content.decode()
        self.assertIn('<a class="skip-link" href="#main">', html)
        self.assertNotIn("left:-9999px", html)
        self.assertIn('id="main"', html)


class NavTests(TestCase):
    def test_toggle_is_associated_with_the_menu_it_controls(self):
        resp = self.client.get(reverse("home"))
        html = resp.content.decode()
        self.assertIn('aria-controls="nav-links"', html)
        self.assertIn('id="nav-links"', html)

    def test_active_nav_item_is_marked_current(self):
        for name, _slot in (
            ("services", "services"),
            ("service_security", "security"),
            ("portfolio", "portfolio"),
            ("blog", "blog"),
        ):
            with self.subTest(page=name):
                resp = self.client.get(reverse(name))
                self.assertContains(resp, 'aria-current="page"')


class BreadcrumbTests(TestCase):
    def test_breadcrumbs_are_a_labelled_list_with_hidden_separators(self):
        resp = self.client.get(reverse("service_networking"))
        html = resp.content.decode()
        self.assertIn('<nav class="crumbs" aria-label="Breadcrumb">', html)
        self.assertIn("<ol>", html)
        # Separators must not be read out as "slash" between each crumb.
        self.assertIn('<span class="sep" aria-hidden="true">/</span>', html)
        self.assertNotIn('<span class="sep">/</span>', html)


class FormErrorTests(TestCase):
    def test_field_errors_are_announced_and_associated(self):
        # Empty POST -> required-field errors on the contact form.
        resp = self.client.post(reverse("contact"), {})
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()

        self.assertIn('id="name-errors"', html)
        self.assertIn('role="alert"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-describedby="name-errors"', html)

        # Every aria-describedby target must actually exist on the page.
        for target in set(re.findall(r'aria-describedby="([^"]+)"', html)):
            for token in target.split():
                with self.subTest(target=token):
                    self.assertIn('id="%s"' % token, html)

    def test_clean_form_has_no_error_attributes(self):
        resp = self.client.get(reverse("contact"))
        html = resp.content.decode()
        self.assertNotIn('aria-invalid="true"', html)
        self.assertNotIn("errorlist", html)

    def test_radio_and_checkbox_groups_use_fieldset_legend(self):
        # An orphan <label> with no `for` names nothing.
        contact = self.client.get(reverse("contact")).content.decode()
        self.assertIn("<legend>For your home or business?</legend>", contact)
        self.assertNotIn("<label>For your home or business?</label>", contact)

        quote = self.client.get(reverse("quote")).content.decode()
        self.assertIn("<legend>What do you need?", quote)
        self.assertNotIn("<label>What do you need?", quote)
