from rest_framework import serializers
from .models import User, UserPreference, PushToken

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['email_notifications', 'push_notifications', 'sms_notifications']

class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ['id', 'token', 'device_type', 'device_id', 'is_active', 'last_used_at', 'created_at']
        read_only_fields = ['id', 'last_used_at', 'created_at']

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    push_token = serializers.CharField(required=False, allow_blank=True)
    preferences = UserPreferenceSerializer(required=False)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'push_token', 'preferences']

    def create(self, validated_data):
        push_token = validated_data.pop('push_token', None)
        preferences_data = validated_data.pop('preferences', {})
        
        user = User.objects.create_user(**validated_data)
        
        # Create preferences
        UserPreference.objects.create(user=user, **preferences_data)
        
        # Create push token if provided
        if push_token:
            PushToken.objects.create(user=user, token=push_token)
        
        return user

class UserSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer(read_only=True)
    push_tokens = PushTokenSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'is_verified', 'preferences', 'push_tokens', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']