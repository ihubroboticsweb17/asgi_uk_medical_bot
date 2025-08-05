from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import RoomDataModel, BedDataModel
from privilagecontroller.views import hasFeatureAccess
from .serializer import RoomDataSerializer, BedDataSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_room(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        try:
            room_count = int(request.data.get('count'))
            if room_count < 1:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'status': 'error', 'message': 'Invalid count provided.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        # Get all rooms created by this user ordered by ID (assumed chronological)
        existing_rooms = RoomDataModel.objects.filter(created_by=request.user).order_by('id')
        existing_count = existing_rooms.count()

        if room_count == existing_count:
            return Response({'status': 'success', 'message': 'Room count matches existing records. No change needed.', 'data': None}, status=status.HTTP_200_OK)

        elif room_count < existing_count:
            # Need to delete rooms beyond the requested count
            rooms_to_delete = existing_rooms[room_count:]  # everything after count
            deleted_data = [RoomDataSerializer(room).data for room in rooms_to_delete]
            for room in rooms_to_delete:
                room.delete()
            return Response({
                'status': 'success',
                'message': f'{existing_count - room_count} room(s) deleted to match the desired count.',
                'data': deleted_data
            }, status=status.HTTP_200_OK)

        else:
            # Need to create new rooms
            rooms_to_create = room_count - existing_count
            new_rooms = []
            for i in range(existing_count + 1, room_count + 1):
                room_name = f"room_{i}"
                new_room = RoomDataModel(room_name=room_name, created_by=request.user, is_active=True)
                new_room.save()
                new_rooms.append(RoomDataSerializer(new_room).data)

            return Response({
                'status': 'success',
                'message': f'{rooms_to_create} room(s) created successfully.',
                'data': new_rooms
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(f"Exception in create_or_update_room: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# READ All Rooms
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_rooms(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        rooms = RoomDataModel.objects.all().order_by('-created_at')
        serializer = RoomDataSerializer(rooms, many=True)
        return Response({'status': 'success', 'message': 'Rooms fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_rooms: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_or_update_bed(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        try:
            bed_count = int(request.data.get('count'))
            if bed_count < 1:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'status': 'error', 'message': 'Invalid count provided.', 'data': None}, status=status.HTTP_400_BAD_REQUEST)

        # Get all rooms created by this user ordered by ID (assumed chronological)
        existing_bed = BedDataModel.objects.filter(created_by=request.user).order_by('id')
        existing_count = existing_bed.count()

        if bed_count == existing_count:
            return Response({'status': 'success', 'message': 'Room count matches existing records. No change needed.', 'data': None}, status=status.HTTP_200_OK)

        elif bed_count < existing_count:
            # Need to delete rooms beyond the requested count
            bed_to_delete = existing_bed[bed_count:]  # everything after count
            deleted_data = [BedDataSerializer(bed).data for bed in bed_to_delete]
            for room in bed_to_delete:
                room.delete()
            return Response({
                'status': 'success',
                'message': f'{existing_count - bed_count} bed(s) deleted to match the desired count.',
                'data': deleted_data
            }, status=status.HTTP_200_OK)

        else:
            # Need to create new rooms
            rooms_to_create = bed_count - existing_count
            new_rooms = []
            for i in range(existing_count + 1, bed_count + 1):
                bed_name = f"bed_{i}"
                new_bed = BedDataModel(bed_name=bed_name, created_by=request.user, is_active=True)
                new_bed.save()
                new_rooms.append(BedDataSerializer(new_bed).data)

            return Response({
                'status': 'success',
                'message': f'{rooms_to_create} beds(s) created successfully.',
                'data': new_rooms
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception(f"Exception in create_or_update_bed: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# READ All Rooms
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_bed(request):
    try:
        if request.user.role not in ['admin', 'nurse']:
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        if not hasFeatureAccess(request.user, 'room_data_handling_crud'):
            return Response({'status': 'error', 'message': 'Permission denied.', 'data': None}, status=status.HTTP_403_FORBIDDEN)

        rooms = BedDataModel.objects.all().order_by('-created_at')
        serializer = BedDataSerializer(rooms, many=True)
        return Response({'status': 'success', 'message': 'Rooms fetched successfully.', 'data': serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f"Exception in view_all_rooms: {e}")
        return Response({'status': 'error', 'message': 'Internal server error.', 'data': None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)