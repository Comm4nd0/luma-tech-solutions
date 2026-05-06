from django import forms

from .models import AUDIENCE_CHOICES, ContactSubmission


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
