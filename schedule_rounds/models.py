from django.db import models
from django.conf import settings
from mainapp.models import Patient

class PatientRoundSchedule(models.Model):
    TIME_SLOT_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='round_schedules'
    )

    time_slot = models.CharField(
        max_length=20,
        choices=TIME_SLOT_CHOICES
    )

    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    trigger_time = models.TimeField()

    is_stopped = models.BooleanField(default=False)
    is_notified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='round_schedules_created',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='round_schedules_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    def __str__(self):
        days = []
        if self.monday: days.append("Mon")
        if self.tuesday: days.append("Tue")
        if self.wednesday: days.append("Wed")
        if self.thursday: days.append("Thu")
        if self.friday: days.append("Fri")
        if self.saturday: days.append("Sat")
        if self.sunday: days.append("Sun")
        
        return f"{self.patient.name} - {self.time_slot} on {', '.join(days)}"