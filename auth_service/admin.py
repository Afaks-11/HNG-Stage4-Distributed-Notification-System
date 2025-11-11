from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PasswordResetToken, EmailVerificationToken, PushToken, NotificationPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model
    """
    list_display = ['email', 'username', 'role', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_verified', 'is_active', 'date_joined']
    search_fields = ['email', 'username', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'phone_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role', 'phone_number'),
        }),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for PasswordResetToken model
    """
    list_display = ['user', 'token', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for EmailVerificationToken model
    """
    list_display = ['user', 'token', 'created_at', 'expires_at', 'is_used']
    list_filter = ['is_used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['token', 'created_at']
    ordering = ['-created_at']


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for PushToken model
    """
    list_display = ['user', 'device_type', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'token', 'device_id']
    readonly_fields = ['created_at', 'updated_at', 'last_used_at']
    ordering = ['-created_at']
    raw_id_fields = ['user']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin interface for NotificationPreference model
    """
    list_display = ['user', 'email_enabled', 'push_enabled', 'quiet_hours_enabled', 'updated_at']
    list_filter = ['email_enabled', 'push_enabled', 'quiet_hours_enabled', 'updated_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    raw_id_fields = ['user']
