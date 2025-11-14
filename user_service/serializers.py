from rest_framework import serializers
from .models import User, UserPreference

class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ['email_notifications', 'push_notifications']

class UserSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer(required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'push_token', 'preferences', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        preferences_data = validated_data.pop('preferences', {})
        password = validated_data.pop('password')
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        UserPreference.objects.create(user=user, **preferences_data)
        return user

class UserCreateSerializer(serializers.ModelSerializer):
    preferences = UserPreferenceSerializer(required=False)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'push_token', 'preferences', 'password']