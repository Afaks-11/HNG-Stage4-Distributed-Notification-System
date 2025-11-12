from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import secrets
import string
from django.core.mail import send_mail

from .models import User, PasswordResetToken, EmailVerificationToken, PushToken, NotificationPreference
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    PushTokenSerializer,
    PushTokenCreateSerializer,
    NotificationPreferenceSerializer,
    UserDetailSerializer,
    UserListSerializer
)
from .utils import create_response, create_pagination_meta
from .permissions import IsOwnerOrAdmin


class StandardPagination(PageNumberPagination):
    """
    Standard pagination class for API responses
    """
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Return a paginated response with standard format
        """
        meta = create_pagination_meta(
            total=self.page.paginator.count,
            limit=self.get_page_size(self.request),
            page=self.page.number
        )
        return create_response(
            success=True,
            message="Data retrieved successfully",
            data=data,
            meta=meta
)


def send_verification_email(user, token):
    verification_url = f"http://localhost:8000/auth/verify/?token={token}"
    subject = "Verify your account"
    message = f"Hi {user.username},\n\nPlease verify your email by clicking the button below:\n{verification_url}\n\nIf you did not sign up, please ignore this email."
    html_message = f"""
        <p>Hi {user.username},</p>
        <p>Please verify your email by clicking the button below:</p>
        <a href='{verification_url}' style='display:inline-block;padding:10px 20px;background:#007bff;color:#fff;text-decoration:none;border-radius:5px;'>Verify Email</a>
        <p>If you did not sign up, please ignore this email.</p>
    """
    send_mail(
        subject,
        message,
        None,
        [user.email],
        html_message=html_message
    )


def send_password_reset_email(user, token):
    reset_url = f"http://localhost:8000/auth/password/reset/confirm/?token={token}"
    subject = "Reset your password"
    message = f"Hi {user.username},\n\nYou requested a password reset. Click the button below to set a new password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
    html_message = f"""
        <p>Hi {user.username},</p>
        <p>You requested a password reset. Click the button below to set a new password:</p>
        <a href='{reset_url}' style='display:inline-block;padding:10px 20px;background:#dc3545;color:#fff;text-decoration:none;border-radius:5px;'>Reset Password</a>
        <p>If you did not request this, please ignore this email.</p>
    """
    send_mail(
        subject,
        message,
        None,
        [user.email],
        html_message=html_message
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for service monitoring
    """
    try:
        # Check database connectivity
        User.objects.first()
        return create_response(
            success=True,
            message="Service is healthy",
            data={
                "status": "healthy",
                "database": "connected",
                "service": "user_service"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        return create_response(
            success=False,
            message="Service is unhealthy",
            error=str(e),
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )


class UserRegistrationView(generics.CreateAPIView):
    """
    View for user registration
    Creates user and automatically creates notification preferences
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create notification preferences for the user
        NotificationPreference.objects.create(user=user)
        
        # Create verification token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        expires_at = timezone.now() + timedelta(hours=24)
        
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Create authentication token
        auth_token, created = Token.objects.get_or_create(user=user)
        
        # Send verification email
        send_verification_email(user, token)
        
        return create_response(
            success=True,
            message="User registered successfully. Please check your email for verification.",
            data={
            'user': UserProfileSerializer(user).data,
            'token': auth_token.key
            },
            status_code=status.HTTP_201_CREATED
        )


class UserLoginView(generics.GenericAPIView):
    """
    View for user login
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return create_response(
            success=True,
            message="Login successful",
            data={
            'user': UserProfileSerializer(user).data,
            'token': token.key
            }
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    """
    View for user logout
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    return create_response(
        success=True,
        message="Logout successful"
    )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for getting and updating user profile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            success=True,
            message="User profile retrieved successfully",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return create_response(
            success=True,
            message="User profile updated successfully",
            data=serializer.data
        )


class ChangePasswordView(generics.UpdateAPIView):
    """
    View for changing password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Delete old token and create new one
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        
        return create_response(
            success=True,
            message="Password changed successfully",
            data={'token': token.key}
        )


class PasswordResetRequestView(generics.GenericAPIView):
    """
    View for requesting password reset
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate reset token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        expires_at = timezone.now() + timedelta(hours=24)
        
        # Create or update reset token
        reset_token, created = PasswordResetToken.objects.get_or_create(
            user=user,
            defaults={'token': token, 'expires_at': expires_at}
        )
        
        if not created:
            reset_token.token = token
            reset_token.expires_at = expires_at
            reset_token.is_used = False
            reset_token.save()
        
        # Send password reset email
        send_password_reset_email(user, token)
        
        return create_response(
            success=True,
            message="Password reset token sent to your email"
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    """
    View for confirming password reset
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Handle GET request when user clicks the reset button in email
        """
        token = request.GET.get('token')
        if not token:
            return create_response(
                success=False,
                message="Token is required",
                error="Token is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if reset_token.is_used:
                return create_response(
                    success=False,
                    message="This reset token has already been used",
                    error="Token already used",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if reset_token.expires_at < timezone.now():
                return create_response(
                    success=False,
                    message="This reset token has expired",
                    error="Token expired",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            return create_response(
                success=True,
                message="Token is valid. You can now set a new password.",
                data={'token': token}
            )
            
        except PasswordResetToken.DoesNotExist:
            return create_response(
                success=False,
                message="Invalid reset token",
                error="Invalid token",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        """
        Handle POST request to set new password
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Get reset token and user
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if reset_token.is_used:
                return create_response(
                    success=False,
                    message="This reset token has already been used",
                    error="Token already used",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if reset_token.expires_at < timezone.now():
                return create_response(
                    success=False,
                    message="This reset token has expired",
                    error="Token expired",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            user = reset_token.user
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Delete old tokens and create new one
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return create_response(
                success=True,
                message="Password reset successful",
                data={'token': token.key}
            )
            
        except PasswordResetToken.DoesNotExist:
            return create_response(
                success=False,
                message="Invalid reset token",
                error="Invalid token",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class EmailVerificationView(generics.GenericAPIView):
    """
    View for email verification
    """
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        verification_token = EmailVerificationToken.objects.get(token=token)
        user = verification_token.user
        
        # Mark user as verified
        user.is_verified = True
        user.save()
        
        # Mark token as used
        verification_token.is_used = True
        verification_token.save()
        
        return create_response(
            success=True,
            message="Email verified successfully!",
            data={'user': UserProfileSerializer(user).data}
        )


class ResendVerificationView(generics.GenericAPIView):
    """
    View for resending verification email
    """
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Delete old verification tokens
        EmailVerificationToken.objects.filter(user=user).delete()
        
        # Create new verification token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        expires_at = timezone.now() + timedelta(hours=24)
        
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Send verification email
        send_verification_email(user, token)
        
        return create_response(
            success=True,
            message="Verification email sent successfully"
        )


class PushTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing push notification tokens
    """
    serializer_class = PushTokenSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        """
        Return push tokens for the current user
        """
        return PushToken.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new push token
        If token already exists for user, update it instead
        """
        serializer = PushTokenCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        device_type = serializer.validated_data.get('device_type', 'web')
        device_id = serializer.validated_data.get('device_id')
        
        # Check if token already exists for this user
        push_token, created = PushToken.objects.get_or_create(
            user=request.user,
            token=token,
            defaults={
                'device_type': device_type,
                'device_id': device_id,
                'is_active': True
            }
        )
        
        if not created:
            # Update existing token
            push_token.device_type = device_type
            push_token.device_id = device_id
            push_token.is_active = True
            push_token.last_used_at = timezone.now()
            push_token.save()
        
        response_serializer = PushTokenSerializer(push_token)
        
        return create_response(
            success=True,
            message="Push token registered successfully" if created else "Push token updated successfully",
            data=response_serializer.data,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def list(self, request, *args, **kwargs):
        """
        List all push tokens for the current user
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            success=True,
            message="Push tokens retrieved successfully",
            data=serializer.data
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific push token
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            success=True,
            message="Push token retrieved successfully",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        """
        Update a push token
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return create_response(
            success=True,
            message="Push token updated successfully",
            data=serializer.data
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete (deactivate) a push token
        """
        instance = self.get_object()
        # Instead of deleting, mark as inactive
        instance.is_active = False
        instance.save()
        
        return create_response(
            success=True,
            message="Push token deactivated successfully"
        )


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    View for getting and updating notification preferences
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get or create notification preferences for the current user
        """
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return create_response(
            success=True,
            message="Notification preferences retrieved successfully",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return create_response(
            success=True,
            message="Notification preferences updated successfully",
            data=serializer.data
        )


class UserDetailView(generics.RetrieveAPIView):
    """
    View for retrieving detailed user information
    Used by API Gateway and other services
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve user details with notification preferences and push tokens
        Only users can view their own data, or admins can view any user
        """
        instance = self.get_object()
        
        # Check if user is viewing their own data or is an admin
        if instance != request.user and not request.user.is_admin:
            return create_response(
                success=False,
                message="You do not have permission to view this user's data",
                error="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance)
        return create_response(
            success=True,
            message="User details retrieved successfully",
            data=serializer.data
        )


class UserListView(generics.ListAPIView):
    """
    View for listing users
    Only accessible by admins
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        """
        Only admins can list users
        """
        if not self.request.user.is_admin:
            return User.objects.none()
        return User.objects.all()

    def list(self, request, *args, **kwargs):
        """
        List users with pagination
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        if not request.user.is_admin:
            return create_response(
                success=False,
                message="You do not have permission to list users",
                error="Permission denied",
                status_code=status.HTTP_403_FORBIDDEN
            )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return create_response(
            success=True,
            message="Users retrieved successfully",
            data=serializer.data
        )
