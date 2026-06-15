"""Form validation: CV magic bytes, postcode normalisation, honeypots."""
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from core.forms import ContactForm, JobApplicationForm, QuoteRequestForm

PDF_BYTES = b"%PDF-1.4\n%fake pdf body for tests\n"
DOCX_BYTES = b"PK\x03\x04" + b"\x00" * 40
OLE_BYTES = b"\xd0\xcf\x11\xe0" + b"\x00" * 40


def _cv(name, content):
    return SimpleUploadedFile(name, content, content_type="application/octet-stream")


class CvValidationTests(TestCase):
    def _form(self, cv):
        return JobApplicationForm(
            data={"name": "A", "email": "a@b.com", "role": "network"},
            files={"cv": cv},
        )

    def test_valid_pdf_passes(self):
        self.assertTrue(self._form(_cv("cv.pdf", PDF_BYTES)).is_valid())

    def test_valid_docx_passes(self):
        self.assertTrue(self._form(_cv("cv.docx", DOCX_BYTES)).is_valid())

    def test_valid_doc_passes(self):
        self.assertTrue(self._form(_cv("cv.doc", OLE_BYTES)).is_valid())

    def test_disallowed_extension_rejected(self):
        form = self._form(_cv("cv.exe", PDF_BYTES))
        self.assertFalse(form.is_valid())
        self.assertIn("cv", form.errors)

    def test_extension_content_mismatch_rejected(self):
        # .pdf extension but ZIP/docx magic bytes -> rejected.
        form = self._form(_cv("cv.pdf", DOCX_BYTES))
        self.assertFalse(form.is_valid())
        self.assertIn("cv", form.errors)

    def test_oversized_rejected(self):
        big = _cv("cv.pdf", PDF_BYTES + b"0" * (5 * 1024 * 1024 + 1))
        form = self._form(big)
        self.assertFalse(form.is_valid())
        self.assertIn("cv", form.errors)

    def test_filename_is_sanitised(self):
        form = self._form(_cv("../../etc/pa ss?wd.pdf", PDF_BYTES))
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data["cv"].name
        self.assertNotIn("/", cleaned)
        self.assertNotIn("?", cleaned)
        self.assertTrue(cleaned.endswith(".pdf"))

    def test_honeypot_blocks_submission(self):
        form = JobApplicationForm(
            data={"name": "A", "email": "a@b.com", "role": "network",
                  "website": "http://spam"},
            files={"cv": _cv("cv.pdf", PDF_BYTES)},
        )
        self.assertFalse(form.is_valid())


class PostcodeTests(TestCase):
    def _form(self, postcode):
        return QuoteRequestForm(data={
            "name": "A", "email": "a@b.com", "postcode": postcode,
            "property_type": "home_small", "services": ["networking"],
        })

    def test_valid_postcode_normalised(self):
        form = self._form("sl71aa")
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["postcode"], "SL7 1AA")

    def test_invalid_postcode_rejected(self):
        form = self._form("NOPE")
        self.assertFalse(form.is_valid())
        self.assertIn("postcode", form.errors)

    def test_services_joined_to_csv(self):
        form = QuoteRequestForm(data={
            "name": "A", "email": "a@b.com", "postcode": "SL7 1AA",
            "property_type": "home_small", "services": ["networking", "security"],
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["services"], "networking,security")

    def test_budget_is_an_accepted_field(self):
        form = QuoteRequestForm(data={
            "name": "A", "email": "a@b.com", "postcode": "SL7 1AA",
            "property_type": "home_small", "services": ["networking"],
            "budget": "5k_15k",
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["budget"], "5k_15k")


class ContactFormTests(TestCase):
    def test_honeypot_blocks_submission(self):
        form = ContactForm(data={
            "name": "A", "email": "a@b.com", "service": "other",
            "message": "hi", "website": "http://spam",
        })
        self.assertFalse(form.is_valid())

    def test_valid_contact(self):
        form = ContactForm(data={
            "name": "A", "email": "a@b.com", "service": "networking",
            "message": "hi",
        })
        self.assertTrue(form.is_valid(), form.errors)
