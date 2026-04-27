from django.db import models


SERVICE_CHOICES = [
    ("networking", "Wi-Fi & Networking"),
    ("development", "App & Web Development"),
    ("automation", "Home Automation"),
    ("support", "Support & Maintenance"),
    ("other", "Something else"),
]


class ContactSubmission(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    service = models.CharField(max_length=32, choices=SERVICE_CHOICES, default="other")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_service_display()}"
