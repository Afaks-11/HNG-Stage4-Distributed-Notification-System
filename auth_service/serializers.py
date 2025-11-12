from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, PasswordResetToken, EmailVerificationToken, PushToken, NotificationPreference


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'role', 'phone_number']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'role': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')

        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'phone_number', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user found with this email address')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if reset_token.is_used:
                raise serializers.ValidationError('Token has already been used')
            if reset_token.is_expired():
                raise serializers.ValidationError('Token has expired')
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError('Invalid token')
        return value 


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification
    """
    token = serializers.CharField()

    def validate_token(self, value):
        try:
            verification_token = EmailVerificationToken.objects.get(token=value)
            if verification_token.is_used:
                raise serializers.ValidationError('Token has already been used')
            if verification_token.is_expired():
                raise serializers.ValidationError('Token has expired')
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError('Invalid verification token')
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification email
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('No user found with this email address')
        return value


class PushTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for push notification tokens
    """
    class Meta:
        model = PushToken
        fields = ['id', 'token', 'device_type', 'device_id', 'is_active', 'created_at', 'updated_at', 'last_used_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_used_at']
    
    def create(self, validated_data):
        # Set user from request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PushTokenCreateSerializer(serializers.Serializer):
    """
    Serializer for creating push tokens
    """
    token = serializers.CharField(max_length=500, required=True)
    device_type = serializers.ChoiceField(choices=['android', 'ios', 'web'], default='web')
    device_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for notification preferences
    """
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'email_marketing', 'email_transactional', 'email_security',
            'push_enabled', 'push_marketing', 'push_transactional', 'push_security',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer for API Gateway and other services
    Includes email and notification preferences
    """
    notification_preferences = NotificationPreferenceSerializer(read_only=True)
    push_tokens = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone_number', 'is_verified',
            'notification_preferences', 'push_tokens', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_push_tokens(self, obj):
        """Return only active push tokens"""
        active_tokens = obj.push_tokens.filter(is_active=True)
        return PushTokenSerializer(active_tokens, many=True).data


class UserListSerializer(serializers.ModelSerializer):
    """
    Lightweight user serializer for listing users
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'is_verified', 'created_at']
        read_only_fields = ['id', 'created_at'] 