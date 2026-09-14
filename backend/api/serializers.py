from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, FarmProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'full_name', 'preferred_language', 'profile_image', 'created_at', 'updated_at')

class FarmProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmProfile
        fields = ('id', 'farm_name', 'location', 'state', 'country', 'farm_area', 'area_unit', 'soil_type', 'irrigation_method', 'main_crops', 'created_at', 'updated_at')

class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'confirm_password', 'full_name')

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError({"email": "A user with that email already exists."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        full_name = validated_data.pop('full_name')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user, full_name=full_name)
        FarmProfile.objects.create(user=user, farm_name=f"{full_name}'s Farm")
        return user
