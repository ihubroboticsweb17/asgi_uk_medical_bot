from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings

class HealthcareUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('nurse', 'Nurse'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=False, blank=False) 
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, null=False, blank=False)
    gender = models.CharField(max_length=100, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # is active is in abstract user
    # username is in abstract user

    REQUIRED_FIELDS = ['name', 'role']

    def __str__(self):
        return f"{self.name} - {self.email} - {self.role}"

class Patient(models.Model):
    patient_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    room_id = models.IntegerField()
    bed_id = models.IntegerField()
    gender = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='patients_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='patients_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} -in room {self.room_id} - in bed {self.bed_id}"

# GENDER_CHOICES = [
#     ('Male', 'Male'),
#     ('Female', 'Female'),
#     ('Non-Binary', 'Non-Binary'),
#     ('Prefer not to say', 'Prefer not to say'),
#     ('Other (Specify)', 'Other (Specify)'),
# ]

# use this to makemigrations
# docker compose run --rm beat python manage.py makemigrations
# docker compose run --rm beat python manage.py makemigrations --empty mainapp
# docker compose run --rm beat python manage.py migrate
# docker compose run --rm beat python manage.py makemigrations
