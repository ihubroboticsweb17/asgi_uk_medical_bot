from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import PatientRoundSchedule
from .serializers import PatientRoundScheduleSerializer
from mainapp.models import Patient
from django.shortcuts import get_object_or_404
from privilagecontroller.views import hasFeatureAccess

@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def create_or_update_round_schedule(request, pk=None):
    
    if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    if not hasFeatureAccess(request.user, 'round_schedule_crud'):
        return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

    if pk:  # Update flow
        instance = get_object_or_404(PatientRoundSchedule, pk=pk)
        serializer = PatientRoundScheduleSerializer(instance, data=request.data, partial=True)
    else:   # Create flow
        serializer = PatientRoundScheduleSerializer(data=request.data)

    if serializer.is_valid():
        if pk:
            serializer.save(updated_by=request.user)
        else:
            serializer.save(created_by=request.user)

        return Response({
            'status': 'success',
            'message': 'Patient round schedule saved successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK if pk else status.HTTP_201_CREATED)

    return Response({
        'status': 'error',
        'message': 'Invalid data.',
        'errors': serializer.errors
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