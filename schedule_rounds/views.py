from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PatientRoundSchedule
from .serializers import PatientRoundScheduleSerializer
from mainapp.models import Patient

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_scheduler(request):
    serializer = PatientRoundScheduleSerializer(data=request.data)

    if serializer.is_valid():
        patient = serializer.validated_data['patient']
        time_slot = serializer.validated_data['time_slot']

        # Days list to check
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        for day in days:
            if serializer.validated_data.get(day):
                filter_kwargs = {
                    'patient': patient,
                    'time_slot': time_slot,
                    day: True
                }
                # Check if record exists for same patient + time slot + day
                existing_schedule = PatientRoundSchedule.objects.filter(**filter_kwargs).first()
                if existing_schedule:
                    # Update existing schedule
                    for field, value in serializer.validated_data.items():
                        setattr(existing_schedule, field, value)
                    existing_schedule.save()
                    return Response({
                        'status': 'success',
                        'message': f"Schedule updated successfully for {day}",
                        'data': PatientRoundScheduleSerializer(existing_schedule).data
                    }, status=status.HTTP_200_OK)

        # If no existing schedule found for any day → create new
        schedule = serializer.save(created_by=request.user)
        return Response({
            'status': 'success',
            'message': 'Schedule created successfully',
            'data': PatientRoundScheduleSerializer(schedule).data
        }, status=status.HTTP_201_CREATED)

    return Response({
        'status': 'error',
        'message': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_scheduled_rounds(request):
    schedules = PatientRoundSchedule.objects.all().order_by('time_slot', 'patient__name')
    serializer = PatientRoundScheduleSerializer(schedules, many=True)
    
    return Response({
        'status': 'success',
        'message': 'All scheduled rounds retrieved successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_patient_scheduled_rounds(request, patient_id):
    if patient_id is None:
        return Response({
            'status': 'success',
            'message': 'Schedule created successfully',
            'data': None
        }, status=status.HTTP_201_CREATED)
    
    schedules = PatientRoundSchedule.objects.filter(patient_id=patient_id)
    serializer = PatientRoundScheduleSerializer(schedules, many=True)
    
    return Response({
        'status': 'success',
        'message': 'Scheduled rounds retrieved successfully',
        'data': serializer.data
    }, status=status.HTTP_200_OK)