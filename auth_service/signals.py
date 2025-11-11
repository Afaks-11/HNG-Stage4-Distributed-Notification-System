from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, NotificationPreference


@receiver(post_save, sender=User)
def create_user_notification_preferences(sender, instance, created, **kwargs):
    """
    Automatically create notification preferences when a user is created
    This ensures preferences exist even if user is created through admin or other means
    """
    if created:
        NotificationPreference.objects.get_or_create(user=instance)

