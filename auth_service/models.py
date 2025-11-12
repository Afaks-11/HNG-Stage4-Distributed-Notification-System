from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with role-based authentication for User Service
    Manages user contact info (email, push tokens), notification preferences, and permissions
    """
    class Role(models.TextChoices):
        CLIENT = 'client', _('Client')
        SUPPLIER = 'supplier', _('Supplier')
        ADMIN = 'admin', _('Admin')

    # Override email to be unique and required
    email = models.EmailField(_('email address'), unique=True)
    
    # Role field for role-based access control
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
        help_text=_('User role in the system')
    )
    
    # Additional fields
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'role']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        db_table = 'users'

    def __str__(self):
        return self.email

    @property
    def is_client(self):
        return self.role == self.Role.CLIENT

    @property
    def is_supplier(self):
        return self.role == self.Role.SUPPLIER

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class PasswordResetToken(models.Model):
    """
    Model for password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('password reset token')
        verbose_name_plural = _('password reset tokens')
        db_table = 'password_reset_tokens'

    def __str__(self):
        return f"Reset token for {self.user.email}"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class EmailVerificationToken(models.Model):
    """
    Model for email verification tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('email verification token')
        verbose_name_plural = _('email verification tokens')
        db_table = 'email_verification_tokens'

    def __str__(self):
        return f"Verification token for {self.user.email}"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at


class PushToken(models.Model):
    """
    Model for storing push notification tokens for users
    Supports multiple devices per user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=500, help_text=_('Device push notification token'))
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('android', 'Android'),
            ('ios', 'iOS'),
            ('web', 'Web'),
        ],
        default='web',
        help_text=_('Type of device')
    )
    device_id = models.CharField(max_length=255, blank=True, null=True, help_text=_('Unique device identifier'))
    is_active = models.BooleanField(default=True, help_text=_('Whether the token is currently active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(blank=True, null=True, help_text=_('Last time this token was used'))

    class Meta:
        verbose_name = _('push token')
        verbose_name_plural = _('push tokens')
        db_table = 'push_tokens'
        unique_together = [['user', 'token']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"Push token for {self.user.email} ({self.device_type})"


class NotificationPreference(models.Model):
    """
    Model for storing user notification preferences
    Controls which types of notifications a user wants to receive
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_enabled = models.BooleanField(default=True, help_text=_('Enable email notifications'))
    email_marketing = models.BooleanField(default=True, help_text=_('Receive marketing emails'))
    email_transactional = models.BooleanField(default=True, help_text=_('Receive transactional emails'))
    email_security = models.BooleanField(default=True, help_text=_('Receive security-related emails'))
    
    # Push preferences
    push_enabled = models.BooleanField(default=True, help_text=_('Enable push notifications'))
    push_marketing = models.BooleanField(default=True, help_text=_('Receive marketing push notifications'))
    push_transactional = models.BooleanField(default=True, help_text=_('Receive transactional push notifications'))
    push_security = models.BooleanField(default=True, help_text=_('Receive security-related push notifications'))
    
    # Quiet hours (optional)
    quiet_hours_enabled = models.BooleanField(default=False, help_text=_('Enable quiet hours'))
    quiet_hours_start = models.TimeField(blank=True, null=True, help_text=_('Start of quiet hours'))
    quiet_hours_end = models.TimeField(blank=True, null=True, help_text=_('End of quiet hours'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('notification preference')
        verbose_name_plural = _('notification preferences')
        db_table = 'notification_preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.email}"
