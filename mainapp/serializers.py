from rest_framework import serializers
from .models import HealthcareUser, Patient
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = HealthcareUser.objects.filter(username=username,is_active=True).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid username or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is deactivated")

        tokens = RefreshToken.for_user(user)
            
        # Update last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        response_data = {
            "user_id": user.pk,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "access_token": str(tokens.access_token),
            "refresh_token": str(tokens),
            "registered_date": user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }

        return response_data

class HealthcareUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthcareUser
        fields = [
            'id',
            'username',
            'password',
            'name',
            'email',
            'role',
            'gender',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Force role to 'admin' regardless of input
        validated_data['role'] = 'admin'
        user = HealthcareUser.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name'],
            email=validated_data['email'],
            gender=validated_data['gender'],
            role=validated_data['role'],
        )
        return user

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'id',
            'patient_id',
            'name',
            'room_id',
            'bed_id',
            'gender',
            'age',
            'is_active',
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by']
