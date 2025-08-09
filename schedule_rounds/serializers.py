from rest_framework import serializers
from .models import PatientRoundSchedule

class PatientRoundScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRoundSchedule
        fields = '__all__'
