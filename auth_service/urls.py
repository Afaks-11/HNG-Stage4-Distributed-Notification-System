"""
URL configuration for Auth Service.
"""
from django.contrib import admin
from django.urls import path, include
from auth_service import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('auth_service.urls')),
    path('health/', views.health_check, name='health'),
]