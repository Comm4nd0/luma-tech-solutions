import os
import re

from django import forms

from .models import AUDIENCE_CHOICES, ContactSubmission, JobApplication


ALLOWED_CV_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_CV_SIZE_BYTES = 5 * 1024 * 1024

# Magic-byte signatures for allowed CV formats.
# PDF:  starts with %PDF
# DOCX: ZIP archive (PK\x03\x04) containing Word XML
# DOC:  OLE2 Compound Document (legacy Word)
_MAGIC_PDF = b"%PDF"
_MAGIC_ZIP = b"PK\x03\x04"       # .docx is a ZIP container
_MAGIC_OLE = b"\xd0\xcf\x11\xe0"  # .doc OLE2 header

# Only these characters are allowed in the sanitised filename that
# gets attached to the notification email.
_SAFE_FILENAME_RE = re.compile(r"[^\w\s\-\.]", re.ASCII)


class ContactForm(forms.ModelForm):
    # Honeypot — bots fill it, humans don't see it.
    website = forms.CharField(required=False, widget=forms.HiddenInput)
    source = forms.CharField(required=False, widget=forms.HiddenInput)

    audience = forms.ChoiceField(
        choices=AUDIENCE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
    )

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "phone", "audience", "service", "message", "source"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your name", "autocomplete": "name"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "you@example.com", "autocomplete": "email"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Optional", "autocomplete": "tel"}
            ),
            "audience": forms.RadioSelect,
            "message": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Tell us a bit about what you need…",
                }
            ),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""


class JobApplicationForm(forms.ModelForm):
    # Honeypot — bots fill it, humans don't see it.
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    cv = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx"}),
        help_text="PDF or Word document, max 5 MB.",
    )

    class Meta:
        model = JobApplication
        fields = ["name", "email", "phone", "role", "cover_note"]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Your name", "autocomplete": "name"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "you@example.com", "autocomplete": "email"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Optional", "autocomplete": "tel"}
            ),
            "cover_note": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Anything you want us to know — relevant experience, availability, why this role appeals to you…",
                }
            ),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""

    def clean_cv(self):
        f = self.cleaned_data.get("cv")
        if not f:
            raise forms.ValidationError("Please attach your CV.")

        # --- size ---
        if f.size > MAX_CV_SIZE_BYTES:
            raise forms.ValidationError("Please keep your CV under 5 MB.")

        # --- filename sanitisation ---
        # Strip any path components the browser might send, reject null bytes.
        name = os.path.basename(f.name or "")
        if "\x00" in name or not name:
            raise forms.ValidationError("Invalid filename.")
        # Normalise to ASCII-safe characters only.
        name = _SAFE_FILENAME_RE.sub("_", name).strip("_. ")
        if not name:
            raise forms.ValidationError("Invalid filename.")
        f.name = name

        # --- extension allowlist ---
        ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if ext not in ALLOWED_CV_EXTENSIONS:
            raise forms.ValidationError(
                "Please upload a PDF or Word document (.pdf, .doc, .docx)."
            )

        # --- magic-byte verification ---
        # Read the first few bytes to confirm the file content matches the
        # claimed extension. Rewind afterwards so the view can .read() later.
        header = f.read(8)
        f.seek(0)
        if len(header) < 4:
            raise forms.ValidationError(
                "The file appears to be empty or corrupt."
            )

        if ext == ".pdf":
            if not header.startswith(_MAGIC_PDF):
                raise forms.ValidationError(
                    "This doesn't look like a valid PDF. "
                    "Please upload a genuine PDF or Word document."
                )
        elif ext == ".docx":
            if not header.startswith(_MAGIC_ZIP):
                raise forms.ValidationError(
                    "This doesn't look like a valid Word document (.docx). "
                    "Please upload a genuine PDF or Word document."
                )
        elif ext == ".doc":
            if not header.startswith(_MAGIC_OLE):
                raise forms.ValidationError(
                    "This doesn't look like a valid Word document (.doc). "
                    "Please upload a genuine PDF or Word document."
                )

        return f
