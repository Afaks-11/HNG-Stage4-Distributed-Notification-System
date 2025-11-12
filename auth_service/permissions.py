from rest_framework import permissions
from .models import User


class IsClient(permissions.BasePermission):
    """
    Permission to check if user is a client
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_client


class IsSupplier(permissions.BasePermission):
    """
    Permission to check if user is a supplier
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_supplier


class IsAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsClientOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a client or admin
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_client or request.user.is_admin)


class IsSupplierOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is a supplier or admin
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_supplier or request.user.is_admin)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to check if user is the owner of the object or admin
    """
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.is_admin:
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'client'):
            return obj.client == request.user
        elif hasattr(obj, 'supplier'):
            return obj.supplier == request.user
        
        return False 