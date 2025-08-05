from rest_framework import serializers
from .models import RoomDataModel, BedDataModel

class RoomDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomDataModel
        fields = '__all__'

class BedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BedDataModel
        fields = '__all__'
