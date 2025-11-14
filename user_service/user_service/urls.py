from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('users/', views.create_user, name='create_user'),
    path('users/<str:user_id>/', views.get_user_profile, name='get_user_profile'),
    path('users/<str:user_id>/preferences/', views.get_user_preferences, name='get_user_preferences'),
]