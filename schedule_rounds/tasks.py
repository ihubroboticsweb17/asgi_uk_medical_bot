from celery import shared_task
from django.utils import timezone
from .models import PatientRoundSchedule
from .serializers import PatientRoundScheduleSerializer
import pytz
from django.core.cache import cache

@shared_task
def check_and_send_schedules():
    # Set the correct timezone (e.g., 'Asia/Kolkata' for IST)
    local_timezone = pytz.timezone('Asia/Kolkata')
    
    # Get the current time in the specified timezone
    now = timezone.localtime(timezone=local_timezone)

    key = f"check_schedule_lock_{now.strftime('%Y%m%d%H%M')}"
    
    # Only one worker can acquire the lock per minute
    if not cache.add(key, "locked", timeout=60):
        print("Another worker already processed this minute, skipping...")
        return
    
    weekday = now.strftime("%A").lower()
    
    schedules = PatientRoundSchedule.objects.filter(**{weekday: True}, is_stopped=False, is_notified=False)

    for schedule in schedules:
        if (schedule.trigger_time.hour == now.hour and schedule.trigger_time.minute == now.minute):
            data = PatientRoundScheduleSerializer(schedule).data
            PatientRoundSchedule.objects.filter(id=schedule.id).update(is_notified=True)
            print(f"scheduler data fetched successfully : {data}")
            # return data


# from celery import shared_task
# from django.utils import timezone
# from .models import PatientRoundSchedule
# from .serializers import PatientRoundScheduleSerializer
# import pytz # Import the pytz library for timezone handling

# @shared_task
# def check_and_send_schedules():
#     # Define the correct timezone for your location (e.g., Asia/Kolkata for IST)
#     local_timezone = pytz.timezone('Asia/Kolkata') 
    
#     # Get the current time and make it timezone-aware
#     now = timezone.localtime(timezone=local_timezone)
    
#     # Extract the current time of day
#     current_time_of_day = now.time()
    
#     weekday = now.strftime("%A").lower()

#     schedules = PatientRoundSchedule.objects.filter(**{weekday: True}, is_stopped=False)
#     print(f"scheduler data outside for loop")

#     for schedule in schedules:
#         print(f"scheduler data in for loop")

#         # Directly compare the time of day objects
#         if schedule.trigger_time.hour == current_time_of_day.hour and schedule.trigger_time.minute == current_time_of_day.minute:
#             data = PatientRoundScheduleSerializer(schedule).data
#             print(f"scheduler data fetched successfully : {data}")
#             return data




# from celery import shared_task
# from django.utils import timezone
# from .models import PatientRoundSchedule
# from .serializers import PatientRoundScheduleSerializer

# @shared_task
# def check_and_send_schedules():
#     now = timezone.localtime()
#     weekday = now.strftime("%A").lower()

#     schedules = PatientRoundSchedule.objects.filter(**{weekday: True}, is_stopped= False)
#     print(f"scheduler data outside for loop")
#     for schedule in schedules:
#         print(f"scheduler data in for loop")
#         if (schedule.trigger_time.hour == now.hour and schedule.trigger_time.minute == now.minute):

#             data = PatientRoundScheduleSerializer(schedule).data
#             print(f"scheduler data fetched successfully : {data}")
#             # return data