from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'auth_service'

# Create router for ViewSets
router = DefaultRouter()
router.register(r'push-tokens', views.PushTokenViewSet, basename='push-token')

urlpatterns = [
    # Health check
    path('health/', views.health_check, name='health_check'),
    
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('me/', views.UserProfileView.as_view(), name='profile'),
    
    # Email verification
    path('verify/', views.EmailVerificationView.as_view(), name='verify_email'),
    path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
    
    # Password management
    path('password/change/', views.ChangePasswordView.as_view(), name='change_password'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Notification preferences
    path('notification-preferences/', views.NotificationPreferenceView.as_view(), name='notification_preferences'),
    
    # User data endpoints (for API Gateway and other services)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:id>/', views.UserDetailView.as_view(), name='user_detail'),
    
    # Include router URLs (push tokens)
    path('', include(router.urls)),
] 