from celery import shared_task
from django.utils import timezone
from .models import PatientRoundSchedule
from .serializers import PatientRoundScheduleSerializer

@shared_task
def check_and_send_schedules():
    now = timezone.localtime()
    weekday = now.strftime("%A").lower()

    schedules = PatientRoundSchedule.objects.filter(**{weekday: True}, is_stopped= False)

    for schedule in schedules:
        if (schedule.trigger_time.hour == now.hour and schedule.trigger_time.minute == now.minute):

            data = PatientRoundScheduleSerializer(schedule).data
            print(f"scheduler data fetched successfully : {data}")
            return data