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

    # def validate(self, data):
    #     room = data.get('room', None)
    #     bed = data.get('bed', None)
        
    #     # No restriction — both can be null, one, or both
    #     # But if you want at least one, add:
    #     # if not room and not bed:
    #     #     raise serializers.ValidationError("Either room or bed must be provided.")

    #     return data