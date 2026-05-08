from django import forms

from .models import AUDIENCE_CHOICES, ContactSubmission, JobApplication


ALLOWED_CV_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_CV_SIZE_BYTES = 5 * 1024 * 1024


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
        if f.size > MAX_CV_SIZE_BYTES:
            raise forms.ValidationError("Please keep your CV under 5 MB.")
        ext = "." + f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
        if ext not in ALLOWED_CV_EXTENSIONS:
            raise forms.ValidationError(
                "Please upload a PDF or Word document (.pdf, .doc, .docx)."
            )
        return f
