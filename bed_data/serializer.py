from rest_framework import serializers
from .models import RoomDataModel, BedDataModel
from mainapp.models import Patient

class RoomDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomDataModel
        fields = '__all__'

class BedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedDataModel
        fields = '__all__'

class PatientRoomBedUpdateSerializer(serializers.ModelSerializer):
    room_id = serializers.PrimaryKeyRelatedField(
        queryset=RoomDataModel.objects.all(),
        source='room',
        required=False,
        allow_null=True
    )
    bed_id = serializers.PrimaryKeyRelatedField(
        queryset=BedDataModel.objects.all(),
        source='bed',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Patient
        fields = ['room_id', 'bed_id']