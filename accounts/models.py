from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} {self.first_name} {self.last_name} {self.email} ({self.role})"


# worker profile
class WorkerProfile(models.Model):
    CATEGORY_CHOICES = [
        ('plumber', 'plumber'),
        ('electrician', 'electrician'),
        ('painter', 'painter'),
        ('carpenter', 'carpenter'),
        ('other', 'other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    experience_years = models.PositiveIntegerField(default=0)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.category}"

