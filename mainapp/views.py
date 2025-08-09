from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication 
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.http import JsonResponse
import time
from asgiref.sync import sync_to_async
from .models import HealthcareUser, Patient
from .serializers import HealthcareUserSerializer, PatientSerializer, LoginSerializer
import logging
from privilagecontroller.views import hasFeatureAccess
logger = logging.getLogger(__name__)
from bed_data.serializer import PatientRoomBedUpdateSerializer
from schedule_rounds.models import PatientRoundSchedule
from django.db import transaction
# if not has_feature_access(request.user, 'view_admin_panel'):
#         return Response({'detail': 'Access Denied'}, status=403)

# Login function
@api_view(['POST'])
@authentication_classes([])  # Disable CSRF-related auth mechanisms
@permission_classes([])  
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response({
            "status": "ok",
            "message": "Login successful",
            "data": serializer.validated_data
        }, status=status.HTTP_200_OK)
    errors = serializer.errors
    first_error = next(iter(errors.values()))[0] if errors else "Invalid input"
    return Response({
        "status": "error",
        "message": first_error
    }, status=status.HTTP_400_BAD_REQUEST)

# Admin/Nurse functions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_admin_data(request):
    try:
        if request.user.role != 'admin':
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('id')

        if user_id:
            try:
                instance = HealthcareUser.objects.get(id=user_id)
            except HealthcareUser.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'User not found.',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = HealthcareUserSerializer(instance, data=request.data, partial=True)
            operation = "updated"
        else:
            serializer = HealthcareUserSerializer(data=request.data)
            operation = "created"

        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': f"User {operation} successfully.",
                'data': serializer.data
            }, status=status.HTTP_200_OK if user_id else status.HTTP_201_CREATED)

        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.exception(f"Exception in create_or_update_admin_data: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_admin_users(request):
    try:
        if request.user.role != 'admin':
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        users = HealthcareUser.objects.all()
        serializer = HealthcareUserSerializer(users, many=True)
        return Response({
            'status': 'success',
            'message': 'Users fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_admin_users: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_admin_user(request, user_id):
    try:
        if request.user.role != 'admin':
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user_instance = HealthcareUser.objects.filter(id=user_id).first()
        if not user_instance:
            return Response({
                'status': 'error',
                'message': 'User not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        user_instance.is_active = not user_instance.is_active
        user_instance.save()
        action = 'activated' if user_instance.is_active else 'deactivated'
        return Response({
            'status': 'success',
            'message': f"User {action} successfully.",
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in soft_delete_admin_user: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Patient functions
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_patient_data(request):
    print("Raw request data:", request.data)
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        patient_id = request.data.get('id')
        room_id = request.data.get('room_id')
        bed_id = request.data.get('bed_id')
        if patient_id:
            try:
                instance = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Patient not found.',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            if instance.room_id != int(room_id) or instance.bed_id != int(bed_id):
                bed_taken = Patient.objects.filter(
                    room_id=room_id,
                    bed_id=bed_id
                ).exclude(id=patient_id).exists()

                if bed_taken:
                    error_msg = f"Bed no. {bed_id} in Room {room_id} already allocated."
                    return Response({
                        'status': 'error',
                        'message': error_msg,
                        'data': None
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            bed_taken = Patient.objects.filter(
                room_id=room_id,
                bed_id=bed_id
            ).exists()
            if bed_taken:
                error_msg = f"Bed no. {bed_id} in Room {room_id} already allocated."
                return Response({
                    'status': 'error',
                    'message': error_msg,
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            if patient_id:
                try:
                    instance = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': 'Patient not found.',
                        'data': None
                    }, status=status.HTTP_404_NOT_FOUND)

                serializer = PatientSerializer(instance, data=request.data, partial=True)
                operation = "updated"
            else:
                serializer = PatientSerializer(data=request.data)
                operation = "created"
            if serializer.is_valid():
                updated_instance = serializer.save(
                    is_active=True,
                    updated_by=request.user if patient_id else None,
                    created_by=request.user if not patient_id else None
                )
                updated_instance.save()
                if not patient_id:
                    default_times = {
                        'morning': "06:00:00",
                        'afternoon': "12:00:00",
                        'evening': "18:00:00",
                        'night': "23:59:59",
                    }
                    schedules = []
                    for slot, _ in PatientRoundSchedule.TIME_SLOT_CHOICES:
                        schedules.append(PatientRoundSchedule(
                            patient=updated_instance,
                            time_slot=slot,
                            monday=False, tuesday=False, wednesday=False,
                            thursday=False, friday=False, saturday=False, sunday=False,
                            trigger_time=default_times[slot],  # default trigger time (you can adjust)
                            created_by=request.user
                        ))
                    PatientRoundSchedule.objects.bulk_create(schedules)
                return Response({
                    'status': 'success',
                    'message': f"Patient {operation} successfully.",
                    'data': serializer.data
                }, status=status.HTTP_200_OK if patient_id else status.HTTP_201_CREATED)
            else:
                return Response({
                    'status': 'error',
                    'message': "Something went wrong",
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'status': 'error',
            'message': 'Validation failed.',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f"Exception in create_or_update_patient_data: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_patient(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        users = Patient.objects.all().order_by('-created_at')
        serializer = PatientSerializer(users, many=True)
        return Response({
            'status': 'success',
            'message': 'Patients fetched successfully.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_patient: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def soft_delete_patient(request, patient_id):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not hasFeatureAccess(request.user, 'patient_data_handling_crud'):
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user_instance = Patient.objects.filter(id=patient_id).first()
        if not user_instance:
            return Response({
                'status': 'error',
                'message': 'User not found.',
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        user_instance.is_active = not user_instance.is_active
        updated_instance = user_instance.save()
        if patient_id:
            updated_instance.updated_by = request.user
        else:
            updated_instance.created_by = request.user
        updated_instance.save() 
        action = 'activated' if user_instance.is_active else 'deactivated'
        return Response({
            'status': 'success',
            'message': f"Patient {action} successfully.",
            'data': None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in soft_delete_admin_user: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def delete_all_patient(request):
    Patient.objects.all().delete()
    return Response({
            'status': 'error',
            'message': 'Internal server error.',
            'data': None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def reassign_designation(request):
    room_id = request.data.get('room_id')
    bed_id = request.data.get('bed_id')
    patient_id = request.data.get('patient_id')

    if request.user.role not in ['admin', 'nurse']:
            return Response({
                'status': 'error',
                'message': 'Permission denied.',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)
    
    if not hasFeatureAccess(request.user, 'reassigning_patient'):
        return Response({
            'status': 'error',
            'message': 'Permission denied.',
            'data': None
        }, status=status.HTTP_403_FORBIDDEN)
    
    has_patient = Patient.objects.filter(patient_id=patient_id).exists()
    if not has_patient:
        return Response({
            'status': 'error',
            'message': 'Select patient to reassign.',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if room_id is None and bed_id is None:
        return Response({
            'status': 'error',
            'message': 'Select either room or bed to reassign.',
            'data': None
        }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = PatientRoomBedUpdateSerializer(patient_id, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save(updated_by=request.user)
        return Response({"message": "Room/Bed updated successfully"})
    return Response(serializer.errors, status=400)