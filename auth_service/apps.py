from django.apps import AppConfig


class AuthServiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_service'

    def ready(self):
        """
        Import signals when app is ready
        """
        import auth_service.signals
