from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserPreference
from .serializers import UserSerializer, UserCreateSerializer
import uuid

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
def register_user(request):
    serializer = UserCreateSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'tokens': tokens
            },
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'error': serializer.errors,
        'message': 'User creation failed'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            'success': False,
            'error': 'Email and password required',
            'message': 'Login failed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=email, password=password)
    if user:
        tokens = get_tokens_for_user(user)
        return Response({
            'success': True,
            'data': {
                'user': UserSerializer(user).data,
                'tokens': tokens
            },
            'message': 'Login successful'
        })
    
    return Response({
        'success': False,
        'error': 'Invalid credentials',
        'message': 'Login failed'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def get_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return Response({
        'success': True,
        'data': UserSerializer(user).data,
        'message': 'User retrieved successfully'
    })

@api_view(['PUT'])
def update_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'User updated successfully'
        })
    
    return Response({
        'success': False,
        'error': serializer.errors,
        'message': 'User update failed'
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def health_check(request):
    return Response({
        'service': 'user-service',
        'status': 'healthy',
        'version': '1.0.0'
    })