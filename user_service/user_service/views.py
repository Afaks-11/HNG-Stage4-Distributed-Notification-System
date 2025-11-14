import requests
from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import json

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "success": True,
        "message": "User Service is healthy",
        "data": {
            "service": "user-service",
            "status": "up",
            "port": 8001
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    return Response({
        "success": True,
        "message": "User created successfully",
        "data": {
            "user_id": "user-123",
            "email": request.data.get('email', 'test@example.com'),
            "name": request.data.get('name', 'Test User')
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_profile(request, user_id):
    return Response({
        "success": True,
        "message": "User profile retrieved successfully",
        "data": {
            "user_id": user_id,
            "name": "Test User",
            "email": "test@example.com",
            "preferences": {
                "email_notifications": True,
                "push_notifications": True
            }
        }
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_preferences(request, user_id):
    return Response({
        "success": True,
        "message": "User preferences retrieved successfully",
        "data": {
            "user_id": user_id,
            "email": "john.doe@example.com",
            "email_notifications": True,
            "push_notifications": True
        }
    })